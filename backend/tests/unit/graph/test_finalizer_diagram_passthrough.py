from app.graph.nodes import finalizer_node


class TestFinalizerDiagramPassthrough:
    def test_diagrams_merged_into_final_proposal(self):
        state = {
            "proposal_draft": {"executive_summary": "draft"},
            "review": {},
            "business_context": {
                "diagram_data": {
                    "workflow_svg": "<svg>workflow</svg>",
                    "timeline_svg": "<svg>timeline</svg>",
                    "architecture_svg": "<svg>arch</svg>",
                }
            },
        }
        result = finalizer_node(state)
        fp = result["final_proposal"]
        assert fp["diagram_data"]["workflow_svg"] == "<svg>workflow</svg>"
        assert fp["diagram_data"]["timeline_svg"] == "<svg>timeline</svg>"
        assert fp["diagram_data"]["architecture_svg"] == "<svg>arch</svg>"

    def test_no_diagrams_does_not_add_key(self):
        state = {
            "proposal_draft": {"executive_summary": "draft"},
            "review": {},
            "business_context": {},
        }
        result = finalizer_node(state)
        assert "diagram_data" not in result["final_proposal"]

    def test_improved_proposal_takes_priority(self):
        state = {
            "proposal_draft": {"executive_summary": "draft"},
            "review": {"improved_proposal": {"executive_summary": "improved"}},
            "business_context": {
                "diagram_data": {"workflow_svg": "<svg>w</svg>"}
            },
        }
        result = finalizer_node(state)
        fp = result["final_proposal"]
        assert fp["executive_summary"] == "improved"
        assert fp["diagram_data"]["workflow_svg"] == "<svg>w</svg>"


class TestFinalizerEngineMerge:
    def _context(self):
        return {
            "pricing_data": {"one_time_cost": 15000, "monthly_cost": 1500},
            "sla_data": {"uptime_guarantee": "99.9%", "sla_tiers": []},
            "timeline_data": {
                "total_duration_months": 4,
                "phases": [
                    {"name": "Design", "duration_weeks": 2, "deliverables": ["Mockups"]},
                    {"name": "Build", "duration_weeks": 4, "deliverables": ["Working MVP", "Mockups"]},
                ],
            },
            "tech_stack_data": {
                "technology_stack": {
                    "frontend": [{"name": "React", "category": "Framework"}],
                    "backend": [{"name": "FastAPI", "category": "Framework"}],
                }
            },
            "module_data": {
                "modules": [
                    {"name": "Inventory", "description": "Stock tracking"},
                    {"name": "Billing", "description": "Invoicing"},
                ]
            },
            "team_data": {
                "team_members": [
                    {"title": "Project Manager", "seniority": "Senior", "allocation": "full_time"},
                ]
            },
            "support_data": {
                "recommended_plan": {
                    "name": "Standard Support",
                    "hours": "12x6",
                    "response_time": "8 hours",
                    "channels": ["Email", "Phone"],
                    "included": ["Bug fixes"],
                }
            },
        }

    def test_engine_sections_merged(self):
        state = {
            "proposal_draft": {"executive_summary": "draft"},
            "review": {},
            "business_context": self._context(),
        }
        fp = finalizer_node(state)["final_proposal"]

        assert fp["pricing"]["one_time_cost"] == 15000
        assert fp["sla"]["uptime_guarantee"] == "99.9%"
        assert fp["timeline"]["total_duration_months"] == 4
        assert fp["technology_stack"]["frontend"] == ["React"]
        assert fp["technology_stack"]["backend"] == ["FastAPI"]
        assert fp["module_breakdown"][0]["module_name"] == "Inventory"
        assert fp["team"][0]["role"] == "Project Manager"
        assert fp["support"]["recommended_plan"] == "Standard Support"
        assert fp["deliverables"] == ["Mockups", "Working MVP"]

    def test_no_business_context_keeps_draft(self):
        state = {
            "proposal_draft": {"executive_summary": "draft"},
            "review": {},
            "business_context": {},
        }
        fp = finalizer_node(state)["final_proposal"]
        assert fp["executive_summary"] == "draft"
        assert "pricing" not in fp
        assert "module_breakdown" not in fp
