import sys; sys.path.insert(0, 'backend')
from app.engines.module_engine import ModuleEngine
from app.engines.industry_engine import IndustryEngine


class TestModuleEngine:
    def setup_method(self):
        self.engine = ModuleEngine()
        self.industry_engine = IndustryEngine()

    def test_healthcare_modules(self):
        ind = self.industry_engine.run({"domain": "healthcare"})
        result = self.engine.run({"industry_data": ind})
        assert result["module_count"] >= 8
        names = [m["name"] for m in result["modules"]]
        assert "Patient Management" in names
        assert "EHR/EMR" in names

    def test_erp_modules(self):
        ind = self.industry_engine.run({"domain": "erp"})
        result = self.engine.run({"industry_data": ind})
        assert result["module_count"] >= 8
        names = [m["name"] for m in result["modules"]]
        assert "Financial Management" in names

    def test_all_industries_have_modules(self):
        for domain in ["healthcare", "erp", "crm", "hrms", "manufacturing",
                       "education", "government", "retail", "logistics",
                       "construction", "finance"]:
            ind = self.industry_engine.run({"domain": domain})
            result = self.engine.run({"industry_data": ind})
            assert result["module_count"] >= 3, f"{domain} has < 3 modules"
