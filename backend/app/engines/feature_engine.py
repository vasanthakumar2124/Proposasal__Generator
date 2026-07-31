from app.engines.base_engine import BaseEngine

COMMON_FEATURES = {
    "user_management": {"name": "User Management", "description": "Registration, login, profile management, role-based access control"},
    "multi_tenant": {"name": "Multi-Tenant Architecture", "description": "Isolated data, custom branding, tenant-level configuration"},
    "audit_logging": {"name": "Audit Logging", "description": "Comprehensive audit trail for all user actions and data changes"},
    "notification": {"name": "Notification Engine", "description": "Email, SMS, push, in-app with template management"},
    "reporting": {"name": "Reporting & Analytics", "description": "Custom reports, dashboards, export (PDF/Excel/CSV)"},
    "api_gateway": {"name": "API Gateway", "description": "RESTful APIs, rate limiting, API key management, documentation"},
    "file_management": {"name": "Document Management", "description": "Upload, versioning, preview, search, secure sharing"},
    "search": {"name": "Advanced Search", "description": "Full-text search, filters, saved searches, faceted navigation"},
    "workflow": {"name": "Workflow Engine", "description": "Configurable approval workflows, task automation, SLA tracking"},
    "import_export": {"name": "Bulk Import/Export", "description": "CSV/Excel import, data mapping, scheduled exports"},
    "mobile": {"name": "Mobile App", "description": "Native mobile apps (iOS/Android) with offline support"},
    "sso": {"name": "Single Sign-On", "description": "SAML, OAuth 2.0, OpenID Connect, LDAP integration"},
    "encryption": {"name": "End-to-End Encryption", "description": "AES-256 at rest, TLS in transit, field-level encryption"},
    "backup": {"name": "Automated Backup", "description": "Scheduled backups, point-in-time recovery, geo-redundancy"},
    "monitoring": {"name": "System Monitoring", "description": "Real-time monitoring, alerts, uptime tracking, APM"},
    "localization": {"name": "Multi-Language", "description": "i18n, RTL support, locale-specific formatting"},
    "dashboard": {"name": "Dashboard", "description": "Role-specific dashboards with KPI widgets and charts"},
    "accessibility": {"name": "Accessibility (WCAG)", "description": "WCAG 2.1 AA compliance, screen reader support, keyboard navigation"},
}


class FeatureEngine(BaseEngine):
    name = "feature"

    def run(self, context: dict) -> dict:
        modules = (context.get("module_data") or {}).get("modules", [])
        industry = (context.get("industry_data") or {}).get("industry", "custom")
        project_type = context.get("project_type", "custom")

        module_names = set(m["name"].lower().replace(" ", "_") for m in modules)

        recommended = []
        for key, feature in COMMON_FEATURES.items():
            relevant = key in module_names
            if relevant or self._is_always_relevant(key, industry, project_type):
                recommended.append(feature)

        industry_specific = self._get_industry_features(industry)

        return {
            "recommended_features": recommended,
            "industry_specific_features": industry_specific,
            "total_features": len(recommended) + len(industry_specific),
            "feature_categories": {
                "core": ["User Management", "Multi-Tenant Architecture", "Audit Logging", "Notification Engine"],
                "business": recommended[4:10] if len(recommended) > 4 else [],
                "compliance": industry_specific,
                "integration": self._get_integration_features(industry),
            },
        }

    def _is_always_relevant(self, key: str, industry: str, project_type: str) -> bool:
        always = {"user_management", "audit_logging", "notification", "reporting", "dashboard", "api_gateway", "backup", "monitoring"}
        return key in always

    def _get_industry_features(self, industry: str) -> list[dict]:
        mapping = {
            "healthcare": [
                {"name": "HIPAA Compliance", "description": "HIPAA-compliant data handling, audit trails, BAA support"},
                {"name": "HL7 FHIR Integration", "description": "Healthcare interoperability standards"},
                {"name": "Patient Data Privacy", "description": "Consent management, data segmentation, access controls"},
            ],
            "finance": [
                {"name": "AML Screening", "description": "Anti-money laundering checks, sanctions screening"},
                {"name": "KYC Verification", "description": "Know Your Customer workflows, document verification"},
                {"name": "Regulatory Reporting", "description": "Automated regulatory filing, audit preparation"},
            ],
            "government": [
                {"name": "FedRAMP Compliance", "description": "FedRAMP authorized cloud infrastructure"},
                {"name": "NIST Controls", "description": "NIST 800-53 security control implementation"},
                {"name": "FOIA Management", "description": "Freedom of Information request processing"},
            ],
            "retail": [
                {"name": "PCI DSS Compliance", "description": "Payment card industry data security"},
                {"name": "Omnichannel Sync", "description": "Real-time inventory and order sync across channels"},
            ],
        }
        return mapping.get(industry, [])

    def _get_integration_features(self, industry: str) -> list[str]:
        mapping = {
            "healthcare": ["EHR/EMR Systems", "Lab Systems", "Pharmacy Systems", "Insurance Portals"],
            "finance": ["Core Banking", "Payment Gateways", "Credit Bureaus", "Regulatory APIs"],
            "erp": ["CRM Systems", "HR Systems", "Banking APIs", "E-procurement"],
            "retail": ["POS Systems", "E-commerce Platforms", "Payment Gateways", "ERP"],
            "logistics": ["Shipping Carriers", "Customs Systems", "Warehouse Systems", "ERP"],
        }
        return mapping.get(industry, ["REST APIs", "Webhooks", "SSO Providers"])
