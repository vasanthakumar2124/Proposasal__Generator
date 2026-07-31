import sys; sys.path.insert(0, 'backend')
from app.engines.proposal_context_builder import ProposalContextBuilder


class TestProposalContextBuilder:
    def setup_method(self):
        self.builder = ProposalContextBuilder()

    def test_full_pipeline_healthcare(self):
        result = self.builder.run({"domain": "healthcare", "project_type": "web_app"})
        assert result["industry_data"]["industry"] == "healthcare"
        assert result["module_data"]["module_count"] > 0
        assert result["feature_data"]["total_features"] > 0
        assert result["pricing_data"]["one_time_cost"] > 0
        assert result["team_data"]["team_size"] > 0
        assert result["timeline_data"]["total_duration_weeks"] > 0
        assert result["roi_data"]["roi_percentage"] is not None
        assert result["risk_data"]["risk_count"] > 0
        assert result["commercial_data"]["payment_terms"] is not None
        assert result["support_data"]["recommended_plan"] is not None
        assert result["sla_data"]["uptime_guarantee"] is not None
        assert set(result["diagram_data"]) == {"workflow_svg", "timeline_svg", "architecture_svg", "mermaid_workflow", "mermaid_timeline"}
        assert result["proposal_summary"]["total_cost"] > 0

    def test_full_pipeline_erp(self):
        result = self.builder.run({"domain": "erp", "project_type": "web_app"})
        assert result["industry_data"]["industry"] == "erp"
        assert result["module_data"]["module_count"] >= 8
        assert result["pricing_data"]["pricing_tier"] in ("premium", "enterprise")

    def test_full_pipeline_custom(self):
        result = self.builder.run({"domain": "custom", "project_type": "web_app"})
        assert result["industry_data"]["industry"] == "custom"
        assert result["proposal_summary"]["module_count"] >= 2

    def test_proposal_summary(self):
        result = self.builder.run({"domain": "healthcare"})
        summary = result["proposal_summary"]
        assert summary["industry"] == "healthcare"
        assert summary["module_count"] > 0
        assert summary["total_cost"] > 0
        assert summary["monthly_cost"] > 0
        assert summary["timeline_months"] > 0
