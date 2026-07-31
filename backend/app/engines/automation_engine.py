from app.engines.base_engine import BaseEngine

AUTOMATION_PATTERNS = {
    "workflow_automation": {
        "name": "Workflow Automation",
        "description": "Automate approval chains, document routing, and task assignments",
        "impact": "high",
        "time_savings": "40% reduction in processing time",
    },
    "data_entry_automation": {
        "name": "Data Entry Automation",
        "description": "OCR, intelligent form filling, automated data extraction",
        "impact": "high",
        "time_savings": "60% reduction in manual data entry",
    },
    "report_generation": {
        "name": "Automated Report Generation",
        "description": "Scheduled report generation, distribution, and alerting",
        "impact": "medium",
        "time_savings": "80% reduction in reporting effort",
    },
    "invoice_processing": {
        "name": "Automated Invoice Processing",
        "description": "PO matching, approval routing, payment scheduling",
        "impact": "high",
        "time_savings": "70% reduction in invoice processing time",
    },
    "customer_onboarding": {
        "name": "Automated Customer Onboarding",
        "description": "Self-service portal, automated verification, welcome sequence",
        "impact": "medium",
        "time_savings": "50% reduction in onboarding time",
    },
    "compliance_monitoring": {
        "name": "Automated Compliance Monitoring",
        "description": "Policy enforcement, automated audits, violation alerts",
        "impact": "high",
        "time_savings": "90% reduction in compliance audit effort",
    },
    "notification_automation": {
        "name": "Intelligent Notification System",
        "description": "Trigger-based multi-channel notifications, escalation management",
        "impact": "medium",
        "time_savings": "30% reduction in manual communication",
    },
    "data_sync": {
        "name": "Automated Data Synchronization",
        "description": "Real-time data sync across systems, conflict resolution",
        "impact": "high",
        "time_savings": "eliminates manual data reconciliation",
    },
}


class AutomationEngine(BaseEngine):
    name = "automation"

    def run(self, context: dict) -> dict:
        industry = (context.get("industry_data") or {}).get("industry", "custom")
        modules = (context.get("module_data") or {}).get("modules", [])

        module_names = " ".join(m["name"].lower() for m in modules)

        applicable = []
        for key, pattern in AUTOMATION_PATTERNS.items():
            relevance = self._calculate_relevance(key, industry, module_names)
            if relevance > 0.3:
                applicable.append({**pattern, "key": key, "relevance_score": round(relevance, 2)})

        applicable.sort(key=lambda x: x["relevance_score"], reverse=True)

        high_impact = [a for a in applicable if a["impact"] == "high"]
        medium_impact = [a for a in applicable if a["impact"] == "medium"]

        return {
            "automation_opportunities": applicable,
            "high_impact": high_impact,
            "medium_impact": medium_impact,
            "total_opportunities": len(applicable),
            "estimated_savings_summary": self._estimate_savings(applicable),
        }

    def _calculate_relevance(self, pattern_key: str, industry: str, module_names: str) -> float:
        keywords = {
            "workflow_automation": ["workflow", "approval", "routing", "process", "task"],
            "data_entry_automation": ["data", "entry", "form", "document", "ocr"],
            "report_generation": ["report", "analytics", "bi", "dashboard"],
            "invoice_processing": ["invoice", "billing", "payment", "finance", "ar"],
            "customer_onboarding": ["onboarding", "customer", "registration", "signup"],
            "compliance_monitoring": ["compliance", "audit", "regulation", "policy"],
            "notification_automation": ["notification", "email", "alert", "communication"],
            "data_sync": ["integration", "sync", "import", "export", "api"],
        }

        words = keywords.get(pattern_key, [])
        matches = sum(1 for w in words if w in module_names)
        return min(1.0, matches / max(len(words), 1)) if words else 0.5

    def _estimate_savings(self, opportunities: list) -> dict:
        total = 0
        count = 0
        for o in opportunities:
            val = o.get("time_savings", "0%")
            if "%" in val:
                try:
                    total += float(val.split("%")[0])
                    count += 1
                except ValueError:
                    pass
        avg = total / max(count, 1)
        return {"average_time_savings": f"{avg:.0f}%", "automation_candidates": len(opportunities)}
