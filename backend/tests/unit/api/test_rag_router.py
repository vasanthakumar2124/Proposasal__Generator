import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config.settings import settings
from app.domain.entities.user import User
from app.rag.router import router
from app.api.deps import get_current_user, get_current_org


class FakeEmbed:
    dimensions = 8

    def embed_query(self, text):
        return [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]


class FakeUser(User):
    def __init__(self, org_id="org-a", user_id="user-1"):
        super().__init__(
            id=user_id,
            organization_id=org_id,
            email=f"{user_id}@test.com",
            name="Test User",
            role="admin",
            password_hash="",
            permissions=[],
            status="active",
        )

    def has_permission(self, permission):
        return True


def make_client(monkeypatch, service, user_org="org-a"):
    monkeypatch.setattr(settings, "QDRANT_URL", "")
    monkeypatch.setattr(settings, "QDRANT_API_KEY", "")
    monkeypatch.setattr("app.rag.router.qdrant_service", service)
    monkeypatch.setattr("app.rag.ingest.qdrant_service", service)
    monkeypatch.setattr("app.rag.service.embedding_service", FakeEmbed())

    app = FastAPI()
    app.include_router(router, prefix="/rag")
    app.dependency_overrides[get_current_user] = lambda: FakeUser(user_org)
    app.dependency_overrides[get_current_org] = lambda: user_org
    return TestClient(app)


def fresh_service():
    return __import__("app.rag.service", fromlist=["QdrantService"]).QdrantService()


class TestRagAuthRequired:
    def test_every_rag_route_401_without_token(self):
        app = FastAPI()
        app.include_router(router, prefix="/rag")
        client = TestClient(app)

        cases = [
            ("GET", "/rag/collections", None),
            ("POST", "/rag/search", {"query": "test", "collection_name": "industry_knowledge"}),
            ("POST", "/rag/ingest", {"content": "test content", "collection_name": "industry_knowledge"}),
            ("POST", "/rag/ingest/file", None),
            ("POST", "/rag/seed", None),
            ("DELETE", "/rag/documents/industry_knowledge/abc123", None),
        ]
        for method, path, body in cases:
            resp = client.request(method, path, json=body)
            assert resp.status_code == 401, f"{method} {path} should 401, got {resp.status_code}"


class TestRagTenantIsolation:
    def test_org_b_cannot_search_org_a_content(self, monkeypatch):
        service = fresh_service()
        client_a = make_client(monkeypatch, service, user_org="org-a")

        ingest = client_a.post(
            "/rag/ingest",
            json={"content": "AcmeCo's secret pricing for the 2026 renewal", "collection_name": "industry_knowledge"},
        )
        assert ingest.status_code == 200, ingest.text
        assert ingest.json()["ingested"] >= 1

        client_b = make_client(monkeypatch, service, user_org="org-b")
        search_b = client_b.post(
            "/rag/search",
            json={"query": "AcmeCo secret pricing", "collection_name": "industry_knowledge"},
        )
        assert search_b.status_code == 200
        assert search_b.json() == []

        search_a = client_a.post(
            "/rag/search",
            json={"query": "AcmeCo secret pricing", "collection_name": "industry_knowledge"},
        )
        assert search_a.status_code == 200
        assert len(search_a.json()) >= 1

    def test_collections_are_org_scoped(self, monkeypatch):
        service = fresh_service()
        client_a = make_client(monkeypatch, service, user_org="org-a")
        client_a.post(
            "/rag/ingest",
            json={"content": "some org a content", "collection_name": "best_practices"},
        )
        collections_b = make_client(monkeypatch, service, user_org="org-b").get("/rag/collections")
        assert collections_b.status_code == 200
        names_b = [c["name"] for c in collections_b.json()]
        assert "best_practices" not in names_b

        collections_a = client_a.get("/rag/collections")
        names_a = [c["name"] for c in collections_a.json()]
        assert "best_practices" in names_a
        assert all("org_a_" not in n and "org_b_" not in n for n in names_a + names_b)
