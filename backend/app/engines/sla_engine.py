from app.engines.base_engine import BaseEngine

SLA_TIERS = {
    "critical": {
        "priority": "Critical",
        "description": "System down or core functionality unavailable",
        "response_time": "30 minutes",
        "resolution_time": "4 hours",
        "notification": "Phone + Email + Slack",
        "escalation": "Immediate escalation to engineering lead",
        "reporting": "Incident report within 24 hours",
    },
    "high": {
        "priority": "High",
        "description": "Major feature impaired, no workaround",
        "response_time": "2 hours",
        "resolution_time": "8 business hours",
        "notification": "Email + Ticket",
        "escalation": "Escalation to senior engineer within 4 hours",
        "reporting": "Incident report within 48 hours",
    },
    "medium": {
        "priority": "Medium",
        "description": "Non-critical feature impaired, workaround available",
        "response_time": "8 business hours",
        "resolution_time": "3 business days",
        "notification": "Ticket System",
        "escalation": "Escalation to engineering team within 2 days",
        "reporting": "Resolved in next release notes",
    },
    "low": {
        "priority": "Low",
        "description": "Cosmetic issues, minor bugs, feature requests",
        "response_time": "24 business hours",
        "resolution_time": "Next release cycle",
        "notification": "Ticket System",
        "escalation": "Product roadmap review",
        "reporting": "Resolved in next release notes",
    },
}


class SLAEngine(BaseEngine):
    name = "sla"

    def run(self, context: dict) -> dict:
        complexity = (context.get("industry_data") or {}).get("complexity", "medium")
        compliance = (context.get("industry_data") or {}).get("compliance_requirements", [])

        uptime_target = "99.95%" if complexity in ("high", "very_high") else "99.9%"
        has_compliance = len(compliance) > 0

        return {
            "uptime_guarantee": uptime_target,
            "service_credits": {
                "below_99.9%": "10% monthly credit",
                "below_99.5%": "25% monthly credit",
                "below_99.0%": "50% monthly credit",
            },
            "sla_tiers": [{"priority": k, **v} for k, v in SLA_TIERS.items()],
            "maintenance_windows": {
                "standard": "Sundays 2:00 AM - 6:00 AM local time",
                "emergency": "Immediate with 2-hour notice for security patches",
                "notice_period": "7 days for scheduled maintenance",
            },
            "compliance_sla": has_compliance,
            "reporting": "Monthly SLA compliance report with uptime statistics",
        }
