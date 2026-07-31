import sys; sys.path.insert(0, 'backend')
from app.engines.industry_engine import IndustryEngine


class TestIndustryEngine:
    def setup_method(self):
        self.engine = IndustryEngine()

    def test_healthcare_industry(self):
        result = self.engine.run({"domain": "healthcare"})
        assert result["industry"] == "healthcare"
        assert "HIPAA" in result["compliance_requirements"]
        assert result["complexity"] == "high"

    def test_erp_industry(self):
        result = self.engine.run({"industry": "ERP"})
        assert result["industry"] == "erp"
        assert "SOX" in result["compliance_requirements"]

    def test_custom_industry(self):
        result = self.engine.run({"domain": "unknown_xyz"})
        assert result["industry"] == "custom"
        assert len(result["compliance_requirements"]) == 0

    def test_alias_resolution(self):
        assert self.engine.run({"domain": "hospital"})["industry"] == "healthcare"
        assert self.engine.run({"domain": "bank"})["industry"] == "finance"
        assert self.engine.run({"domain": "school"})["industry"] == "education"

    def test_all_industries_have_data(self):
        for alias, resolved in [
            ("healthcare", "healthcare"), ("erp", "erp"), ("crm", "crm"),
            ("hrms", "hrms"), ("manufacturing", "manufacturing"),
            ("retail", "retail"), ("logistics", "logistics"),
            ("education", "education"), ("government", "government"),
            ("construction", "construction"), ("finance", "finance"),
        ]:
            result = self.engine.run({"domain": alias})
            assert result["industry"] == resolved
            assert len(result["compliance_requirements"]) >= 0
