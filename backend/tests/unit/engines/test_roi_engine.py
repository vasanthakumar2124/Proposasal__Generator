import sys; sys.path.insert(0, 'backend')
from app.engines.roi_engine import ROIEngine


class TestROIEngine:
    def setup_method(self):
        self.engine = ROIEngine()

    def test_roi_calculation(self):
        result = self.engine.run({
            "industry_data": {"industry": "healthcare", "compliance_requirements": ["HIPAA"]},
            "pricing_data": {"one_time_cost": 100000, "monthly_cost": 3000, "annual_cost": 136000},
            "automation_data": {},
        })
        assert result["roi_percentage"] is not None
        assert result["payback_period_months"] > 0
        assert len(result["roi_metrics"]) == 5

    def test_different_industries(self):
        for industry in ["healthcare", "erp", "crm", "retail"]:
            result = self.engine.run({
                "industry_data": {"industry": industry},
                "pricing_data": {"one_time_cost": 50000, "monthly_cost": 1500, "annual_cost": 68000},
                "automation_data": {},
            })
            assert result["roi_percentage"] is not None
