from app.engines.base_engine import BaseEngine


class CommercialEngine(BaseEngine):
    name = "commercial"

    def run(self, context: dict) -> dict:
        pricing = context.get("pricing_data", {})

        return {
            "payment_terms": [
                {"term": "Project Initiation", "percentage": 30, "description": "Due upon signing to commence project", "trigger": "Contract signing"},
                {"term": "Milestone 1 Completion", "percentage": 30, "description": "Due upon delivery of Foundation phase", "trigger": "Foundation phase sign-off"},
                {"term": "Milestone 2 Completion", "percentage": 25, "description": "Due upon delivery of Feature Development phase", "trigger": "Feature phase sign-off"},
                {"term": "Final Delivery & Go-Live", "percentage": 15, "description": "Due upon successful go-live and acceptance", "trigger": "UAT sign-off and deployment"},
            ],
            "billing_cycle": "Monthly for ongoing services",
            "invoice_terms": "Net 30 from invoice date",
            "late_payment_terms": "1.5% monthly interest on overdue amounts",
            "currency": "USD",
            "taxes": "Applicable taxes (VAT/Sales Tax) will be added separately",
            "additional_costs": [
                "Third-party licensing fees (if any) passed through at cost",
                "Travel and accommodation for on-site visits (if required)",
                "Additional integrations beyond scope quoted separately",
            ],
            "payment_options": pricing.get("payment_options", []),
        }
