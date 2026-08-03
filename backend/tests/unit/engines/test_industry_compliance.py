import sys; sys.path.insert(0, 'backend')
from app.engines.industry_engine import IndustryEngine


class FakeLLM:
    def __init__(self, result):
        self.result = result

    def generate_json(self, prompt, **kwargs):
        return self.result


class TestIndustryCompliance:
    def setup_method(self):
        self.engine = IndustryEngine()

    def test_car_marketplace_gets_no_retail_compliance(self):
        result = self.engine.run({
            "domain": "custom",
            "description": "Peer-to-peer car marketplace where users list used cars, search with filters, and chat with sellers.",
        })
        assert "GS1" not in result["applicable_standards"]
        assert "EDI" not in result["applicable_standards"]

    def test_payment_project_gets_pci_dss(self):
        result = self.engine.run({
            "domain": "custom",
            "description": "Online store with checkout, card payments, and order tracking.",
        })
        assert "PCI DSS" in result["compliance_requirements"]

    def test_healthcare_project_gets_hipaa(self):
        result = self.engine.run({
            "domain": "custom",
            "description": "Hospital appointment scheduling app storing patient medical records.",
        })
        assert "HIPAA" in result["compliance_requirements"]

    def test_llm_output_overrides_heuristics(self):
        engine = IndustryEngine(FakeLLM({"compliance": ["PCI DSS", "GDPR"], "standards": []}))
        result = engine.run({
            "domain": "retail",
            "description": "Point of sale system for a boutique clothing store.",
        })
        assert result["compliance_requirements"] == ["PCI DSS", "GDPR"]

    def test_llm_empty_result_falls_back_to_heuristics(self):
        engine = IndustryEngine(FakeLLM({"compliance": [], "standards": []}))
        result = engine.run({
            "domain": "custom",
            "description": "Hospital scheduling app storing patient data.",
        })
        assert "HIPAA" in result["compliance_requirements"]

    def test_no_description_uses_pattern_fallback(self):
        result = self.engine.run({"domain": "finance"})
        assert result["compliance_requirements"]

    def test_clean_list_filters_junk(self):
        out = IndustryEngine._clean_list([" PCI DSS ", "PCI DSS", "", "x" * 80, 123])
        assert out == ["PCI DSS"]
