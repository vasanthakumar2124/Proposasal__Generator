from app.engines.base_engine import BaseEngine

INTEGRATION_CATALOG = {
    "payment": [
        {"name": "Stripe", "type": "Payment Gateway", "description": "Credit card, subscription, invoice payments"},
        {"name": "PayPal", "type": "Payment Gateway", "description": "Digital wallet and payment processing"},
        {"name": "Braintree", "type": "Payment Gateway", "description": "Merchant account and payment gateway"},
    ],
    "communication": [
        {"name": "SendGrid", "type": "Email Service", "description": "Transactional and marketing email delivery"},
        {"name": "Twilio", "type": "SMS/Voice", "description": "SMS notifications, voice calls, 2FA"},
        {"name": "Slack", "type": "Messaging", "description": "Team notifications and alerting"},
        {"name": "Push Notifications", "type": "Mobile", "description": "Firebase Cloud Messaging / APNs"},
    ],
    "storage": [
        {"name": "AWS S3", "type": "Object Storage", "description": "Scalable file and document storage"},
        {"name": "Cloudflare R2", "type": "Object Storage", "description": "S3-compatible storage, zero egress fees"},
        {"name": "Azure Blob", "type": "Object Storage", "description": "Microsoft cloud object storage"},
    ],
    "auth": [
        {"name": "Auth0", "type": "Identity", "description": "Authentication, SSO, MFA, user management"},
        {"name": "Keycloak", "type": "Identity", "description": "Open-source identity and access management"},
        {"name": "Google OAuth", "type": "Social Login", "description": "Google sign-in integration"},
    ],
    "analytics": [
        {"name": "Google Analytics", "type": "Web Analytics", "description": "User behavior and traffic analysis"},
        {"name": "Mixpanel", "type": "Product Analytics", "description": "User engagement and retention analytics"},
        {"name": "PostHog", "type": "Product Analytics", "description": "Self-hosted product analytics platform"},
    ],
    "monitoring": [
        {"name": "Datadog", "type": "APM", "description": "Application performance monitoring and logs"},
        {"name": "Sentry", "type": "Error Tracking", "description": "Real-time error tracking and debugging"},
        {"name": "Grafana", "type": "Monitoring", "description": "Metrics visualization and alerting"},
    ],
    "crm": [
        {"name": "Salesforce", "type": "CRM", "description": "Enterprise CRM and sales management"},
        {"name": "HubSpot", "type": "CRM", "description": "Marketing, sales, and service hub"},
    ],
    "erp": [
        {"name": "SAP", "type": "ERP", "description": "Enterprise resource planning integration"},
        {"name": "Oracle ERP", "type": "ERP", "description": "Oracle Cloud ERP integration"},
        {"name": "Microsoft Dynamics", "type": "ERP", "description": "Dynamics 365 integration"},
    ],
}

INDUSTRY_INTEGRATIONS = {
    "healthcare": ["payment", "communication", "storage", "auth", "monitoring", "crm"],
    "finance": ["payment", "communication", "storage", "auth", "monitoring", "analytics"],
    "erp": ["payment", "communication", "storage", "auth", "monitoring", "crm", "erp"],
    "crm": ["payment", "communication", "storage", "auth", "monitoring", "analytics"],
    "retail": ["payment", "communication", "storage", "auth", "monitoring", "analytics"],
    "logistics": ["payment", "communication", "storage", "auth", "monitoring"],
    "government": ["communication", "storage", "auth", "monitoring"],
    "education": ["payment", "communication", "storage", "auth", "monitoring", "analytics"],
}


class IntegrationEngine(BaseEngine):
    name = "integration"

    def run(self, context: dict) -> dict:
        industry = (context.get("industry_data") or {}).get("industry", "custom")
        required_categories = INDUSTRY_INTEGRATIONS.get(industry, ["payment", "communication", "storage", "auth", "monitoring"])

        recommended = []
        for category in required_categories:
            options = INTEGRATION_CATALOG.get(category, [])
            for opt in options[:2]:
                recommended.append(opt)

        return {
            "integrations": recommended,
            "integration_categories": required_categories,
            "total_integrations": len(recommended),
            "integration_approach": "API-first with webhook support for real-time sync",
        }
