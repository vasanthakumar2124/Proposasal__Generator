import sys; sys.path.insert(0, 'backend')
from app.engines.risk_engine import RiskEngine


class TestRiskEngine:
    def setup_method(self):
        self.engine = RiskEngine()

    def test_common_risks_returned(self):
        result = self.engine.run({"industry_data": {"industry": "custom", "complexity": "medium"}})
        assert result["risk_count"] >= 10
        assert len(result["critical_risks"]) >= 1
        assert "categorized_risks" in result

    def test_healthcare_has_compliance_risk(self):
        result = self.engine.run({"industry_data": {"industry": "healthcare", "complexity": "high"}})
        risks = [r["risk"] for r in result["risks"]]
        assert "HIPAA Compliance Violation" in risks

    def test_risk_summary_structure(self):
        result = self.engine.run({"industry_data": {"industry": "finance", "complexity": "very_high"}})
        summary = result["risk_summary"]
        assert "critical" in summary
        assert "high" in summary
        assert summary["critical"] + summary["high"] > 0
