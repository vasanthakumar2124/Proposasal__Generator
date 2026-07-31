from app.engines.base_engine import BaseEngine

HOURLY_RATES = {
    "project_manager": 85,
    "solution_architect": 95,
    "frontend_dev": 65,
    "backend_dev": 75,
    "uiux_designer": 60,
    "qa_engineer": 55,
    "devops_engineer": 80,
    "ai_engineer": 100,
    "data_engineer": 85,
    "security_engineer": 95,
}

TIER_PRICING = {
    "basic": {"one_time": 5000, "monthly": 500, "support_hours": 10},
    "standard": {"one_time": 15000, "monthly": 1500, "support_hours": 30},
    "premium": {"one_time": 35000, "monthly": 3500, "support_hours": 60},
    "enterprise": {"one_time": 75000, "monthly": 7500, "support_hours": 120},
}

MODULE_EFFORT_MAPPING = {
    "core": {"hours_per_module": 80, "roles": ["project_manager", "solution_architect", "backend_dev", "frontend_dev"]},
    "advanced": {"hours_per_module": 120, "roles": ["backend_dev", "frontend_dev", "ai_engineer", "qa_engineer"]},
    "integration": {"hours_per_module": 60, "roles": ["backend_dev", "devops_engineer"]},
    "ai": {"hours_per_module": 160, "roles": ["ai_engineer", "data_engineer", "backend_dev"]},
    "mobile": {"hours_per_module": 200, "roles": ["frontend_dev", "backend_dev", "qa_engineer"]},
}


class PricingEngine(BaseEngine):
    name = "pricing"

    def run(self, context: dict) -> dict:
        modules = (context.get("module_data") or {}).get("modules", [])
        features = (context.get("feature_data") or {}).get("recommended_features", [])
        complexity = (context.get("industry_data") or {}).get("complexity", "medium")

        base_cost, breakdown = self._calculate_effort_cost(modules)
        tier = self._determine_tier(features, complexity)
        tier_pricing = TIER_PRICING[tier]

        one_time = tier_pricing["one_time"] + base_cost
        monthly = tier_pricing["monthly"] + round(base_cost * 0.015)

        return {
            "pricing_tier": tier,
            "tier_label": tier.capitalize(),
            "one_time_cost": one_time,
            "monthly_cost": monthly,
            "annual_cost": one_time + monthly * 12,
            "five_year_tco": one_time + monthly * 60,
            "total_effort_hours": sum(b["hours"] for b in breakdown.values()),
            "effort_breakdown": breakdown,
            "hourly_rates": HOURLY_RATES,
            "support_hours_included": tier_pricing["support_hours"],
            "payment_options": [
                {"type": "Full Payment", "description": "100% upfront", "amount": one_time, "savings": 0},
                {"type": "Milestone Based", "description": "30% start + 40% mid + 30% completion", "amount": one_time, "savings": 0},
                {"type": "Monthly Subscription", "description": f"{monthly}/month for 12 months", "amount": monthly * 12, "savings": 0},
            ],
        }

    def _calculate_effort_cost(self, modules: list) -> tuple[int, dict]:
        total_hours = 0
        total_cost = 0
        breakdown = {}

        for module in modules:
            name = module.get("name", "").lower()
            type_key = "core"
            for key in MODULE_EFFORT_MAPPING:
                if key in name:
                    type_key = key
                    break

            effort = MODULE_EFFORT_MAPPING[type_key]
            hours = effort["hours_per_module"]
            role_costs = [HOURLY_RATES.get(r, 60) for r in effort["roles"]]
            avg_rate = sum(role_costs) / len(role_costs)
            cost = round(hours * avg_rate)

            total_hours += hours
            total_cost += cost
            breakdown[module.get("name", f"Module_{len(breakdown)}")] = {
                "hours": hours,
                "hourly_rate": round(avg_rate),
                "cost": cost,
                "type": type_key,
            }

        return total_cost, breakdown

    def _determine_tier(self, features: list, complexity: str) -> str:
        feature_names = " ".join(f.get("name", "") for f in features).lower()
        has_ai = "ai" in feature_names or "ml" in feature_names
        has_advanced = any(x in feature_names for x in ["advanced", "analytics", "reporting"])
        has_enterprise = any(x in feature_names for x in ["enterprise", "compliance", "audit"])

        if has_enterprise or complexity == "very_high":
            return "enterprise"
        if has_ai and has_advanced:
            return "premium"
        if has_advanced:
            return "standard"
        return "basic"
