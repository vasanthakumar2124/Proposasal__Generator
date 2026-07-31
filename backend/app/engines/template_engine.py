from app.engines.base_engine import BaseEngine

DEFAULT_TEMPLATE = {
    "sections": [
        {"key": "cover_page", "label": "Cover Page", "order": 0, "required": True, "generated_by": "system"},
        {"key": "table_of_contents", "label": "Table of Contents", "order": 1, "required": True, "generated_by": "system"},
        {"key": "executive_summary", "label": "Executive Summary", "order": 2, "required": True, "generated_by": "llm"},
        {"key": "client_understanding", "label": "Client Understanding", "order": 3, "required": True, "generated_by": "llm"},
        {"key": "business_objectives", "label": "Business Objectives", "order": 4, "required": True, "generated_by": "engine"},
        {"key": "current_challenges", "label": "Current Challenges", "order": 5, "required": True, "generated_by": "engine"},
        {"key": "proposed_solution", "label": "Proposed Solution", "order": 6, "required": True, "generated_by": "llm"},
        {"key": "project_scope", "label": "Project Scope", "order": 7, "required": True, "generated_by": "engine"},
        {"key": "modules", "label": "Modules", "order": 8, "required": True, "generated_by": "engine"},
        {"key": "features", "label": "Feature List", "order": 9, "required": True, "generated_by": "engine"},
        {"key": "automation_opportunities", "label": "Automation Opportunities", "order": 10, "required": False, "generated_by": "engine"},
        {"key": "technology_stack", "label": "Technology Stack", "order": 11, "required": True, "generated_by": "engine"},
        {"key": "architecture", "label": "Architecture & Workflow", "order": 12, "required": True, "generated_by": "engine"},
        {"key": "diagrams", "label": "Diagrams", "order": 13, "required": True, "generated_by": "engine"},
        {"key": "timeline", "label": "Timeline", "order": 14, "required": True, "generated_by": "engine"},
        {"key": "implementation_methodology", "label": "Implementation Methodology", "order": 15, "required": True, "generated_by": "engine"},
        {"key": "resource_plan", "label": "Resource Plan", "order": 16, "required": True, "generated_by": "engine"},
        {"key": "pricing", "label": "Pricing", "order": 17, "required": True, "generated_by": "engine"},
        {"key": "commercials", "label": "Commercials & Payment Terms", "order": 18, "required": True, "generated_by": "engine"},
        {"key": "support", "label": "Support & Warranty", "order": 19, "required": True, "generated_by": "engine"},
        {"key": "sla", "label": "Service Level Agreement", "order": 20, "required": False, "generated_by": "engine"},
        {"key": "risk_analysis", "label": "Risk Analysis", "order": 21, "required": True, "generated_by": "engine"},
        {"key": "roi", "label": "Return on Investment", "order": 22, "required": True, "generated_by": "engine"},
        {"key": "future_enhancements", "label": "Future Enhancements", "order": 23, "required": False, "generated_by": "engine"},
        {"key": "conclusion", "label": "Conclusion", "order": 24, "required": True, "generated_by": "llm"},
    ],
    "styling": {
        "primary_color": "#2563eb",
        "secondary_color": "#7c3aed",
        "font_family": "Inter, sans-serif",
        "page_size": "A4",
        "cover_page_style": "professional",
    },
}


class TemplateEngine(BaseEngine):
    name = "template"

    def __init__(self):
        self.default = DEFAULT_TEMPLATE

    def run(self, context: dict) -> dict:
        template_id = context.get("template_id")
        if template_id:
            pass  # In production, load from DB

        return {
            "template_id": template_id or "default",
            "sections_config": self.default["sections"],
            "styling": {**self.default["styling"], **(context.get("branding") or {})},
            "section_order": [s["key"] for s in sorted(self.default["sections"], key=lambda x: x["order"])],
            "enabled_sections": [s for s in self.default["sections"] if s["required"] or True],
        }
