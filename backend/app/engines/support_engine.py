from app.engines.base_engine import BaseEngine

SUPPORT_TIERS = {
    "basic": {
        "name": "Basic Support",
        "hours": "8x5 (Business Hours)",
        "response_time": "24 hours",
        "channels": ["Email"],
        "included": ["Bug fixes", "Critical issue resolution", "Email support"],
        "excluded": ["Feature requests", "Training", "Customization"],
        "monthly_cost": 500,
    },
    "standard": {
        "name": "Standard Support",
        "hours": "12x6 (Extended Hours)",
        "response_time": "8 hours critical, 24 hours standard",
        "channels": ["Email", "Phone", "Ticket System"],
        "included": ["Bug fixes", "Critical issue resolution", "Email & phone support", "Quarterly health check"],
        "excluded": ["Feature requests", "Training"],
        "monthly_cost": 1500,
    },
    "premium": {
        "name": "Premium Support",
        "hours": "24x7",
        "response_time": "1 hour critical, 4 hours high, 8 hours standard",
        "channels": ["Email", "Phone", "Ticket System", "Slack/Dedicated Channel"],
        "included": ["Bug fixes", "Critical issue resolution", "24/7 support", "Monthly health check", "Dedicated account manager", "Priority feature requests"],
        "excluded": [],
        "monthly_cost": 3500,
    },
    "enterprise": {
        "name": "Enterprise Support",
        "hours": "24x7 with Named Support Engineer",
        "response_time": "30 min critical, 2 hours high, 4 hours standard",
        "channels": ["Email", "Phone", "Ticket System", "Slack/Dedicated Channel", "On-site (quarterly)"],
        "included": ["Everything in Premium", "Named support engineer", "Weekly health check", "On-site visits", "Proactive monitoring", "SLA guarantees"],
        "excluded": [],
        "monthly_cost": 7500,
    },
}


class SupportEngine(BaseEngine):
    name = "support"

    def run(self, context: dict) -> dict:
        pricing = context.get("pricing_data", {})
        tier = pricing.get("pricing_tier", "standard")

        if tier not in SUPPORT_TIERS:
            tier = "standard"

        recommended = SUPPORT_TIERS[tier]
        all_tiers = [v for k, v in SUPPORT_TIERS.items()]

        return {
            "recommended_plan": recommended,
            "available_plans": all_tiers,
            "included_in_plan": recommended.get("included", []),
        }
