import pytest


class FakeLLM:
    def __init__(self, extraction, enrichment=None):
        self.extraction = extraction
        self.enrichment = enrichment
        self.calls = []

    def generate_json(self, prompt, complexity="simple", max_tokens=2048):
        self.calls.append(prompt)
        if "infer reasonable assumptions" in prompt.lower() or "REQUIREMENT_ENRICHMENT_TEMPLATE" in prompt:
            return self.enrichment or {"assumptions": ["Assumption: the client will provide product data feeds."]}
        return self.extraction


class TestRequirementAgentDefaults:
    def test_no_input_returns_defaults(self):
        from app.llm import LLMClient
        from app.agents.requirement_agent import RequirementAgent
        agent = RequirementAgent(LLMClient())
        result = agent.run({"raw_client_input": ""})
        reqs = result.get("requirements", {})
        assert reqs.get("domain") == "custom"
        assert reqs.get("project_type") == "web_app"


class TestRequirementAgentEnrichment:
    def _agent(self, description, features):
        from app.agents.requirement_agent import RequirementAgent

        extraction = {
            "project_name": "Thin Project",
            "domain": "custom",
            "project_type": "web_app",
            "description": description,
            "core_features": features,
            "target_audience": "users",
        }
        return RequirementAgent(FakeLLM(extraction))

    def test_thin_input_infers_assumptions(self):
        agent = self._agent("Build a website.", ["login"])
        result = agent.run({"raw_client_input": "Build a website."})
        reqs = result["requirements"]
        assert len(reqs["assumptions"]) >= 1
        assert "Assumption:" in reqs["assumptions"][0]
        assert len(agent.llm.calls) == 2

    def test_short_description_triggers_enrichment(self):
        agent = self._agent(
            "Website.",  # 1 word
            ["login", "dashboard", "reporting"],
        )
        result = agent.run({"raw_client_input": "Website."})
        assert "assumptions" in result["requirements"]

    def test_rich_input_skips_enrichment(self):
        agent = self._agent(
            "An internal logistics platform with route optimization, live driver tracking, "
            "automated invoicing, and a fleet dashboard for the operations team.",
            ["route optimization", "driver tracking", "invoicing", "fleet dashboard"],
        )
        result = agent.run({"raw_client_input": "logistics"})
        assert "assumptions" not in result["requirements"]
        assert len(agent.llm.calls) == 1

    def test_enrichment_failure_keeps_requirements(self):
        from app.agents.requirement_agent import RequirementAgent

        extraction = {
            "project_name": "Thin",
            "domain": "custom",
            "project_type": "web_app",
            "description": "A portal.",
            "core_features": ["login"],
        }

        class BoomLLM(FakeLLM):
            def generate_json(self, prompt, complexity="simple", max_tokens=2048):
                self.calls.append(prompt)
                if len(self.calls) > 1:
                    raise RuntimeError("quota")
                return self.extraction

        agent = RequirementAgent(BoomLLM(extraction))
        result = agent.run({"raw_client_input": "A portal."})
        reqs = result["requirements"]
        assert reqs["project_name"] == "Thin"
        assert "assumptions" not in reqs
