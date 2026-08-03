from app.agents.rag_agent import RAGAgent
from app.llm import LLMClient


class TestRAGCaseStudies:
    def test_case_studies_populated_from_chunks(self):
        agent = RAGAgent(LLMClient())
        result = agent.run({
            "rag_chunks": [],
            "case_study_chunks": [
                "Car marketplace doubled listings in 6 months. Full story here.",
                "A dealership portal cut manual work by 40%.",
            ],
            "requirements": {"domain": "automotive", "description": "test"},
        })
        cs = result.get("rag_context", {}).get("relevant_case_studies")
        assert cs is not None
        assert len(cs) == 2
        assert cs[0]["title"].startswith("Car marketplace doubled listings")
        assert "dealership" in cs[1]["description"]

    def test_no_case_study_chunks_stays_empty(self):
        agent = RAGAgent(LLMClient())
        result = agent.run({
            "rag_chunks": [],
            "case_study_chunks": [],
            "requirements": {"domain": "healthcare", "description": "test"},
        })
        assert result["rag_context"]["relevant_case_studies"] == []

    def test_llm_path_keeps_llm_case_studies(self):
        class FakeLLM:
            def generate_json(self, prompt, complexity="simple", max_tokens=1024):
                return {
                    "domain_insights": ["Healthcare insights"],
                    "relevant_case_studies": [
                        {"title": "Hospital rollout", "description": "From the LLM"},
                    ],
                }

        agent = RAGAgent(FakeLLM())
        result = agent.run({
            "rag_chunks": ["some chunk"],
            "case_study_chunks": ["Deterministic fallback should NOT override the LLM."],
            "requirements": {"domain": "healthcare", "description": "test"},
        })
        cs = result["rag_context"]["relevant_case_studies"]
        assert cs == [{"title": "Hospital rollout", "description": "From the LLM"}]
