import pytest
from app.export.normalize import normalize_proposal


class TestNormalizeProposal:
    def test_executive_summary_string_is_not_triplicated(self):
        result = normalize_proposal({"executive_summary": "summary text"})
        es = result["executive_summary"]
        assert es["business_overview"] == "summary text"
        assert es["problem_statement"] == ""
        assert es["proposed_solution"] == ""

    def test_project_overview_maps_to_client_understanding(self):
        data = {
            "project_overview": {
                "background": "client background",
                "objectives": ["goal1"],
                "scope": "in scope",
                "out_of_scope": ["out1"],
            }
        }
        result = normalize_proposal(data)
        assert "project_overview" not in result
        assert result["client_understanding"]["business_overview"] == "client background"
        assert result["client_understanding"]["business_goals"] == ["goal1"]
        assert result["requirement_analysis"]["scope"] == "in scope"
        assert result["requirement_analysis"]["out_of_scope"] == ["out1"]

    def test_technical_approach_maps_correctly(self):
        data = {
            "technical_approach": {
                "architecture": "microservices",
                "tech_stack": ["Python", "FastAPI"],
                "methodology": "agile",
                "development_phases": [
                    {"phase": "Phase 1", "duration": "2 weeks", "description": "setup"}
                ],
            }
        }
        result = normalize_proposal(data)
        assert "technical_approach" not in result
        assert result["proposed_solution"]["architecture"] == "microservices"
        assert result["technology_stack"]["backend"] == ["Python", "FastAPI"]
        assert result["methodology"]["phases"] == ["Phase 1"]

    def test_core_features_list_maps_to_module_breakdown(self):
        data = {
            "core_features": [
                {"name": "Auth", "description": "login", "benefit": "secure"},
                {"name": "Payment", "description": "pay", "benefit": "fast"},
            ]
        }
        result = normalize_proposal(data)
        assert result["module_breakdown"][0]["module_name"] == "Auth"
        assert result["module_breakdown"][0]["description"] == "login"
        assert result["module_breakdown"][1]["benefit"] == "fast"

    def test_implementation_plan_maps_to_project_plan(self):
        data = {
            "implementation_plan": {
                "timeline": "12 weeks",
                "milestones": ["M1", "M2"],
                "team": "5 developers",
            }
        }
        result = normalize_proposal(data)
        assert "implementation_plan" not in result
        assert result["project_plan"]["timeline"] == "12 weeks"
        assert result["project_plan"]["milestones"] == ["M1", "M2"]
        assert result["project_plan"]["team"] == "5 developers"

    def test_why_choose_us_maps_to_about_company(self):
        data = {
            "why_choose_us": {
                "expertise": "we know stuff",
                "approach": "agile approach",
                "support": "24/7 support",
            }
        }
        result = normalize_proposal(data)
        assert "why_choose_us" not in result
        assert "about_company" in result
        assert result["about_company"]["why_choose_us"] == [
            "we know stuff", "agile approach", "24/7 support"
        ]

    def test_next_steps_list_appended_to_conclusion(self):
        result = normalize_proposal({"next_steps": ["Sign", "Pay"]})
        assert result["conclusion"]["next_steps"] == ["Sign", "Pay"]

    def test_diagram_data_flattened(self):
        result = normalize_proposal({
            "diagram_data": {
                "workflow_svg": "<svg>workflow</svg>",
                "timeline_svg": "<svg>timeline</svg>",
            }
        })
        assert result["workflow_diagram_svg"] == "<svg>workflow</svg>"
        assert result["timeline_diagram_svg"] == "<svg>timeline</svg>"
        assert "diagram_data" not in result
