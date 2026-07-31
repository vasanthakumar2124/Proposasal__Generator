import pytest


class TestRequirementAgentDefaults:
    def test_no_input_returns_defaults(self):
        from app.llm import LLMClient
        from app.agents.requirement_agent import RequirementAgent
        agent = RequirementAgent(LLMClient())
        result = agent.run({"raw_client_input": ""})
        reqs = result.get("requirements", {})
        assert reqs.get("domain") == "custom"
        assert reqs.get("project_type") == "web_app"
