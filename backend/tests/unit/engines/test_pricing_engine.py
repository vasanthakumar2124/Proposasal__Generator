import sys; sys.path.insert(0, 'backend')
from app.engines.pricing_engine import PricingEngine


class TestPricingEngine:
    def setup_method(self):
        self.engine = PricingEngine()

    def test_basic_pricing(self):
        result = self.engine.run({
            "module_data": {"modules": [{"name": "User Management"}]},
            "feature_data": {"recommended_features": [{"name": "Login"}]},
            "industry_data": {"complexity": "low"},
        })
        assert result["one_time_cost"] > 0
        assert result["monthly_cost"] > 0
        assert result["pricing_tier"] in ("basic", "standard")

    def test_enterprise_pricing(self):
        result = self.engine.run({
            "module_data": {"modules": [{"name": "User Management"}, {"name": "AI Analytics"}]},
            "feature_data": {"recommended_features": [
                {"name": "AI Assistant"}, {"name": "Advanced Analytics"}
            ]},
            "industry_data": {"complexity": "very_high"},
        })
        assert result["pricing_tier"] == "enterprise"

    def test_payment_options(self):
        result = self.engine.run({
            "module_data": {"modules": [{"name": "Core Module"}]},
            "feature_data": {"recommended_features": []},
            "industry_data": {"complexity": "medium"},
        })
        assert len(result["payment_options"]) == 3
