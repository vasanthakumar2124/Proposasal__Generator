PRICING_TIERS = {
    "basic": {
        "label": "Basic",
        "one_time": 5000,
        "monthly": 500,
        "features_included": ["core_features"],
    },
    "standard": {
        "label": "Standard",
        "one_time": 15000,
        "monthly": 1500,
        "features_included": ["core_features", "admin_features", "reporting_features"],
    },
    "premium": {
        "label": "Premium",
        "one_time": 35000,
        "monthly": 3500,
        "features_included": [
            "core_features", "admin_features", "customer_features",
            "reporting_features", "security_features", "ai_features",
        ],
    },
    "enterprise": {
        "label": "Enterprise",
        "one_time": 75000,
        "monthly": 7500,
        "features_included": ["all"],
    },
}

HOURLY_RATES = {
    "project_manager": 85,
    "solution_architect": 95,
    "frontend_dev": 65,
    "backend_dev": 75,
    "uiux_designer": 60,
    "qa_engineer": 55,
    "devops": 80,
    "ai_engineer": 100,
}

MODULE_ESTIMATES = {
    "user_management": {"hours": 60, "roles": ["backend_dev", "frontend_dev"]},
    "authentication": {"hours": 30, "roles": ["backend_dev"]},
    "dashboard": {"hours": 50, "roles": ["frontend_dev", "uiux_designer"]},
    "reporting": {"hours": 80, "roles": ["backend_dev", "frontend_dev"]},
    "api_integration": {"hours": 40, "roles": ["backend_dev"]},
    "ai_features": {"hours": 120, "roles": ["ai_engineer", "backend_dev"]},
    "mobile_app": {"hours": 200, "roles": ["frontend_dev", "backend_dev"]},
    "payment": {"hours": 40, "roles": ["backend_dev", "devops"]},
    "notification": {"hours": 30, "roles": ["backend_dev", "frontend_dev"]},
    "admin_panel": {"hours": 60, "roles": ["frontend_dev", "backend_dev"]},
}


def calculate_effort_cost(features: dict) -> dict:
    total_hours = 0
    total_cost = 0
    breakdown = {}

    feature_keys = set()
    for category, items in features.items():
        if isinstance(items, list):
            feature_keys.update(items)

    for module, estimate in MODULE_ESTIMATES.items():
        hours = estimate["hours"]
        role_cost = sum(HOURLY_RATES.get(r, 60) for r in estimate["roles"])
        cost = hours * role_cost
        total_hours += hours
        total_cost += cost
        breakdown[module] = {
            "hours": hours,
            "hourly_rate": role_cost,
            "cost": cost,
        }

    return {
        "total_hours": total_hours,
        "total_cost": total_cost,
        "monthly_maintenance": round(total_cost * 0.015),
        "breakdown": breakdown,
    }


def get_pricing_tier(features: dict) -> str:
    has_ai = any("ai" in k.lower() for k in features.keys())
    has_admin = any("admin" in k.lower() for k in features.keys())
    has_customer = any("customer" in k.lower() for k in features.keys())
    has_security = any("security" in k.lower() for k in features.keys())

    if has_ai and has_customer and has_security:
        return "enterprise" if has_ai else "premium"
    if has_admin and has_customer:
        return "premium"
    if has_admin:
        return "standard"
    return "basic"


def generate_pricing_section(features: dict) -> dict:
    tier_key = get_pricing_tier(features)
    tier = PRICING_TIERS[tier_key]
    effort = calculate_effort_cost(features)

    return {
        "tier": tier_key,
        "tier_label": tier["label"],
        "one_time_cost": tier["one_time"] + effort["total_cost"],
        "monthly_cost": tier["monthly"] + effort["monthly_maintenance"],
        "total_effort_hours": effort["total_hours"],
        "effort_breakdown": effort["breakdown"],
        "payment_options": [
            {"type": "one_time", "amount": tier["one_time"] + effort["total_cost"]},
            {"type": "monthly", "amount": tier["monthly"] + effort["monthly_maintenance"], "term": 12},
        ],
    }
