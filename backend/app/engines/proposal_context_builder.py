from app.engines.base_engine import BaseEngine
from app.engines.industry_engine import IndustryEngine
from app.engines.module_engine import ModuleEngine
from app.engines.feature_engine import FeatureEngine
from app.engines.automation_engine import AutomationEngine
from app.engines.integration_engine import IntegrationEngine
from app.engines.tech_stack_engine import TechStackEngine
from app.engines.timeline_engine import TimelineEngine
from app.engines.pricing_engine import PricingEngine
from app.engines.team_engine import TeamEngine
from app.engines.roi_engine import ROIEngine
from app.engines.risk_engine import RiskEngine
from app.engines.commercial_engine import CommercialEngine
from app.engines.support_engine import SupportEngine
from app.engines.sla_engine import SLAEngine
from app.engines.diagram_engine import DiagramEngine
from app.engines.template_engine import TemplateEngine


class ProposalContextBuilder(BaseEngine):
    """Orchestrates all business engines to build complete proposal context.
    Zero LLM calls — pure deterministic Python.
    """

    name = "context_builder"

    def __init__(self):
        self.engines = {
            "industry": IndustryEngine(),
            "modules": ModuleEngine(),
            "features": FeatureEngine(),
            "automation": AutomationEngine(),
            "integrations": IntegrationEngine(),
            "tech_stack": TechStackEngine(),
            "timeline": TimelineEngine(),
            "pricing": PricingEngine(),
            "team": TeamEngine(),
            "roi": ROIEngine(),
            "risk": RiskEngine(),
            "commercials": CommercialEngine(),
            "support": SupportEngine(),
            "sla": SLAEngine(),
            "diagrams": DiagramEngine(),
            "template": TemplateEngine(),
        }

    def run(self, context: dict) -> dict:
        result = {}

        result["industry_data"] = self.engines["industry"].run(context)

        context_with_industry = {**context, "industry_data": result["industry_data"]}
        result["module_data"] = self.engines["modules"].run(context_with_industry)

        context_with_modules = {**context_with_industry, "module_data": result["module_data"]}
        result["feature_data"] = self.engines["features"].run(context_with_modules)

        context_with_features = {**context_with_modules, "feature_data": result["feature_data"]}
        result["automation_data"] = self.engines["automation"].run(context_with_features)
        result["integration_data"] = self.engines["integrations"].run(context_with_features)
        result["tech_stack_data"] = self.engines["tech_stack"].run(context_with_features)
        result["timeline_data"] = self.engines["timeline"].run(context_with_features)
        result["pricing_data"] = self.engines["pricing"].run(context_with_features)

        context_with_pricing = {
            **context_with_features,
            "pricing_data": result["pricing_data"],
            "tech_stack_data": result["tech_stack_data"],
            "timeline_data": result["timeline_data"],
        }
        result["team_data"] = self.engines["team"].run(context_with_pricing)
        result["roi_data"] = self.engines["roi"].run(context_with_pricing)
        result["risk_data"] = self.engines["risk"].run(context_with_pricing)
        result["commercial_data"] = self.engines["commercials"].run(context_with_pricing)
        result["support_data"] = self.engines["support"].run(context_with_pricing)
        result["sla_data"] = self.engines["sla"].run(context_with_pricing)
        result["diagram_data"] = self.engines["diagrams"].run(context_with_pricing)
        result["template_data"] = self.engines["template"].run(context_with_pricing)

        result["proposal_summary"] = self._build_summary(result)

        return result

    def _build_summary(self, engine_results: dict) -> dict:
        return {
            "industry": engine_results.get("industry_data", {}).get("industry", "custom"),
            "module_count": engine_results.get("module_data", {}).get("module_count", 0),
            "feature_count": engine_results.get("feature_data", {}).get("total_features", 0),
            "automation_count": engine_results.get("automation_data", {}).get("total_opportunities", 0),
            "total_team_size": engine_results.get("team_data", {}).get("team_size", 0),
            "total_cost": engine_results.get("pricing_data", {}).get("one_time_cost", 0),
            "monthly_cost": engine_results.get("pricing_data", {}).get("monthly_cost", 0),
            "timeline_months": engine_results.get("timeline_data", {}).get("total_duration_months", 0),
            "roi_pct": engine_results.get("roi_data", {}).get("roi_percentage", 0),
            "payback_months": engine_results.get("roi_data", {}).get("payback_period_months", 0),
            "risk_count": engine_results.get("risk_data", {}).get("risk_count", 0),
        }
