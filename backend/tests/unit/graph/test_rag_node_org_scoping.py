import pytest

from app.config.settings import settings


class FakeEmbed:
    dimensions = 8

    def embed_query(self, text):
        return [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]


class FakeRAGAgent:
    def run(self, state):
        return state


DISTINCTIVE_FACT = (
    "Orbital Dynamics framework is the secret internal methodology of Meridian Corp. "
    "It reduces project overruns by thirty percent."
)


@pytest.fixture
def rag_env(monkeypatch):
    monkeypatch.setattr(settings, "QDRANT_URL", "")
    monkeypatch.setattr(settings, "QDRANT_API_KEY", "")
    from app.rag.service import embedding_service
    from app.rag import qdrant_service

    monkeypatch.setattr("app.rag.service.embedding_service", FakeEmbed())
    monkeypatch.setattr("app.graph.nodes.rag_agent", FakeRAGAgent())

    qdrant_service._client = None
    qdrant_service._initialized = False
    qdrant_service.initialize()
    return qdrant_service


class TestRagNodeOrgScoping:
    def test_org_knowledge_surfaces_in_generation(self, monkeypatch, rag_env):
        from app.graph.nodes import rag_node

        org_id = "org-test-1"
        rag_env.insert_document(
            "best_practices",
            DISTINCTIVE_FACT,
            {"source": "uploaded.pdf"},
            org_id=org_id,
        )

        state = rag_node({
            "raw_client_input": "Build a satellite tracking platform using Orbital Dynamics",
            "organization_id": org_id,
            "requirements": {
                "domain": "aerospace",
                "description": "Orbital Dynamics satellite tracking platform",
                "project_type": "web_app",
            },
            "rag_context": None,
            "business_context": None,
            "proposal_draft": None,
            "review": None,
            "final_proposal": None,
            "error": None,
        })

        chunks = state["rag_chunks"]
        assert any("Orbital Dynamics" in c for c in chunks), f"org fact missing from rag chunks: {chunks}"

    def test_other_org_knowledge_never_leaks(self, monkeypatch, rag_env):
        from app.graph.nodes import rag_node

        rag_env.insert_document(
            "best_practices",
            DISTINCTIVE_FACT,
            {"source": "uploaded.pdf"},
            org_id="org-secret",
        )

        state = rag_node({
            "raw_client_input": "Build a satellite tracking platform using Orbital Dynamics",
            "organization_id": "org-test-2",
            "requirements": {
                "domain": "aerospace",
                "description": "Orbital Dynamics satellite tracking platform",
                "project_type": "web_app",
            },
            "rag_context": None,
            "business_context": None,
            "proposal_draft": None,
            "review": None,
            "final_proposal": None,
            "error": None,
        })

        assert not any("Orbital Dynamics" in c for c in state["rag_chunks"])
