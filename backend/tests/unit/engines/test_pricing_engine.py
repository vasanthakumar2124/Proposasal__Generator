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

    def test_word_boundary_classification_no_false_ai(self):
        # "ai" must not match "airline" or "maintenance"
        assert self.engine._classify_module("Airline Booking") == "core"
        assert self.engine._classify_module("Maintenance Management") == "core"
        assert self.engine._classify_module("AI Diagnostics") == "ai"
        assert self.engine._classify_module("Mobile App Module") == "mobile"
        assert self.engine._classify_module("Payment Integration") == "integration"

    def test_complexity_multiplier_scales_hours(self):
        low = self.engine.run({
            "module_data": {"modules": [{"name": "User Management"}]},
            "feature_data": {"recommended_features": []},
            "industry_data": {"complexity": "low"},
        })
        high = self.engine.run({
            "module_data": {"modules": [{"name": "User Management"}]},
            "feature_data": {"recommended_features": []},
            "industry_data": {"complexity": "very_high"},
        })
        low_hours = low["effort_breakdown"]["User Management"]["hours"]
        high_hours = high["effort_breakdown"]["User Management"]["hours"]
        assert high_hours > low_hours
        assert high_hours == 104  # 80 * 1.3
        assert low_hours == 68  # 80 * 0.85
