from app.engines.base_engine import BaseEngine

COMMON_RISKS = [
    {
        "risk": "Scope Creep",
        "category": "Project Management",
        "probability": "high",
        "impact": "high",
        "mitigation": "Agile methodology with strict sprint boundaries, change control process, and regular stakeholder reviews",
        "contingency": "Buffer of 15% in timeline and budget for scope adjustments",
    },
    {
        "risk": "Technology Integration Challenges",
        "category": "Technical",
        "probability": "medium",
        "impact": "high",
        "mitigation": "Proof of concept for critical integrations, API-first approach, comprehensive integration testing",
        "contingency": "Alternative integration paths and fallback mechanisms",
    },
    {
        "risk": "Resource Availability",
        "category": "Resource",
        "probability": "medium",
        "impact": "medium",
        "mitigation": "Resource planning with buffer, cross-training team members, partner agreements for scaling",
        "contingency": "Pre-qualified contractor bench for rapid scaling",
    },
    {
        "risk": "Data Migration Complexity",
        "category": "Technical",
        "probability": "medium",
        "impact": "high",
        "mitigation": "Early data audit, phased migration strategy, data validation at each step",
        "contingency": "Rollback procedures and parallel system operation during transition",
    },
    {
        "risk": "User Adoption Resistance",
        "category": "Organizational",
        "probability": "medium",
        "impact": "medium",
        "mitigation": "Change management program, training sessions, user champions program, intuitive UX design",
        "contingency": "Extended support period and additional training sessions",
    },
    {
        "risk": "Security Vulnerabilities",
        "category": "Security",
        "probability": "low",
        "impact": "critical",
        "mitigation": "Secure coding practices, regular penetration testing, code reviews, dependency scanning",
        "contingency": "Incident response plan, bug bounty program",
    },
    {
        "risk": "Regulatory Compliance Gaps",
        "category": "Compliance",
        "probability": "low",
        "impact": "critical",
        "mitigation": "Compliance requirements built into design phase, regular compliance audits, legal review",
        "contingency": "Compliance remediation sprint in project plan",
    },
    {
        "risk": "Performance Bottlenecks",
        "category": "Technical",
        "probability": "medium",
        "impact": "medium",
        "mitigation": "Performance testing at every sprint, scalable architecture design, CDN and caching strategy",
        "contingency": "Performance optimization sprint, auto-scaling infrastructure",
    },
    {
        "risk": "Third-Party Dependency Failure",
        "category": "Technical",
        "probability": "low",
        "impact": "high",
        "mitigation": "Vendor assessment, SLAs with vendors, abstraction layers for third-party services",
        "contingency": "Alternative vendor evaluation, graceful degradation design",
    },
    {
        "risk": "Timeline Overrun",
        "category": "Project Management",
        "probability": "medium",
        "impact": "high",
        "mitigation": "Realistic estimation with buffers, weekly progress tracking, early warning system",
        "contingency": "Priority-based feature trimming, additional sprints if needed",
    },
]

INDUSTRY_RISKS = {
    "healthcare": [
        {"risk": "HIPAA Compliance Violation", "category": "Compliance", "probability": "low", "impact": "critical",
         "mitigation": "HIPAA-compliant architecture, BAAs with all vendors, regular compliance audits",
         "contingency": "Immediate remediation protocol, breach notification plan"},
        {"risk": "Patient Data Migration Errors", "category": "Data", "probability": "medium", "impact": "high",
         "mitigation": "Data validation framework, phased migration, parallel system operation",
         "contingency": "Data rollback capability, extended validation period"},
    ],
    "finance": [
        {"risk": "Regulatory Reporting Failure", "category": "Compliance", "probability": "low", "impact": "critical",
         "mitigation": "Automated regulatory checks, audit trails, real-time compliance monitoring",
         "contingency": "Manual reporting fallback, regulatory liaison"},
        {"risk": "Financial Data Integrity Issue", "category": "Data", "probability": "low", "impact": "critical",
         "mitigation": "Double-entry validation, reconciliation automation, immutable audit logs",
         "contingency": "Transaction rollback, reconciliation process"},
    ],
    "government": [
        {"risk": "Security Clearance Delays", "category": "Compliance", "probability": "medium", "impact": "high",
         "mitigation": "Early clearance initiation, pre-vetted team members",
         "contingency": "Backup team members with clearances"},
    ],
}


class RiskEngine(BaseEngine):
    name = "risk"

    def run(self, context: dict) -> dict:
        industry = (context.get("industry_data") or {}).get("industry", "custom")
        complexity = (context.get("industry_data") or {}).get("complexity", "medium")

        risks = list(COMMON_RISKS)
        industry_specific = INDUSTRY_RISKS.get(industry, [])
        risks.extend(industry_specific)

        if complexity in ("high", "very_high"):
            risks.append({
                "risk": "Increased Complexity Risk",
                "category": "Project Management",
                "probability": "high",
                "impact": "high",
                "mitigation": "Dedicated solution architect, phased delivery, continuous stakeholder alignment",
                "contingency": "Extended architecture phase, additional technical leads",
            })

        categorized = {}
        for r in risks:
            cat = r["category"]
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(r)

        critical_risks = [r for r in risks if r["impact"] == "critical"]
        high_risks = [r for r in risks if r["impact"] == "high"]

        return {
            "risks": risks,
            "risk_count": len(risks),
            "categorized_risks": categorized,
            "critical_risks": critical_risks,
            "high_risks": high_risks,
            "risk_summary": {
                "critical": len(critical_risks),
                "high": len(high_risks),
                "medium": len([r for r in risks if r["impact"] == "medium"]),
                "low": len([r for r in risks if r["impact"] == "low"]),
            },
        }
