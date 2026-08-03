from app.engines.tech_stack_engine import TechStackEngine


class FakeLLM:
    def __init__(self, result=None):
        self.result = result or {"rationale": "React 19 matches the marketplace UI needs while FastAPI serves the API reliably."}
        self.calls = []

    def generate_json(self, prompt, complexity="simple", max_tokens=1024):
        self.calls.append(prompt)
        return self.result


class TestTechStackEngine:
    def setup_method(self):
        self.engine = TechStackEngine()

    def test_default_web_app(self):
        result = self.engine.run({"description": "Build a website"})
        assert "React 19" in {i["name"] for i in result["technology_stack"]["frontend"]}
        assert result["rationale"]

    def test_saas_platform_alias_resolves_to_saas(self):
        result = self.engine.run({"project_type": "saas_platform", "description": "Multi-tenant SaaS"})
        assert "Stripe" in {i["name"] for i in result["technology_stack"]["backend"]}

    def test_ecommerce_template(self):
        result = self.engine.run({"project_type": "ecommerce", "description": "Online store"})
        assert "Stripe" in {i["name"] for i in result["technology_stack"]["backend"]}
        assert "Elasticsearch" in {i["name"] for i in result["technology_stack"]["database"]}

    def test_mobile_template(self):
        result = self.engine.run({"project_type": "mobile_app", "description": "Mobile app"})
        assert "React Native" in {i["name"] for i in result["technology_stack"]["frontend"]}

    def test_unknown_type_falls_back_to_web_app(self):
        result = self.engine.run({"project_type": "quantum", "description": "x"})
        assert "React 19" in {i["name"] for i in result["technology_stack"]["frontend"]}

    def test_llm_rationale_used_when_present(self):
        engine = TechStackEngine(llm=FakeLLM())
        result = engine.run({
            "project_type": "ecommerce",
            "domain": "retail",
            "description": "An online store with product search and Stripe checkout.",
        })
        assert "React 19" in result["rationale"]

    def test_llm_failure_falls_back_to_deterministic_rationale(self):
        class BoomLLM(FakeLLM):
            def generate_json(self, *a, **k):
                raise RuntimeError("quota")

        engine = TechStackEngine(llm=BoomLLM())
        result = engine.run({"project_type": "web_app", "description": "A website"})
        assert result["rationale"]
        assert "React" in result["rationale"] or "stack" in result["rationale"]

    def test_no_description_skips_llm(self):
        class TrackLLM(FakeLLM):
            pass

        engine = TechStackEngine(llm=TrackLLM())
        result = engine.run({"project_type": "web_app", "description": ""})
        assert result["rationale"]
        assert engine.llm.calls == []
