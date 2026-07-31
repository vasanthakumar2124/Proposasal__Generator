class TestRAGAgentDefaults:
    def test_no_chunks_returns_empty(self):
        from app.llm import LLMClient
        from app.agents.rag_agent import RAGAgent
        agent = RAGAgent(LLMClient())
        result = agent.run({
            "rag_chunks": [],
            "requirements": {"domain": "healthcare", "description": "test"},
        })
        ctx = result.get("rag_context", {})
        assert ctx.get("domain_insights") == []
        assert ctx.get("key_considerations") == []
