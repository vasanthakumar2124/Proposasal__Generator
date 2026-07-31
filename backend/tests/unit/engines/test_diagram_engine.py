import sys; sys.path.insert(0, 'backend')
from app.engines.diagram_engine import DiagramEngine


class TestDiagramEngine:
    def setup_method(self):
        self.engine = DiagramEngine()

    def test_all_diagram_types_returned(self):
        result = self.engine.run({
            "module_data": {"modules": [{"name": "Test Module"}]},
            "tech_stack_data": {},
            "timeline_data": {"phases": [{"name": "Phase 1", "duration_weeks": 2}]},
        })
        assert "workflow_svg" in result
        assert "timeline_svg" in result
        assert "architecture_svg" in result
        assert "mermaid_workflow" in result
        assert "mermaid_timeline" in result

    def test_workflow_svg_is_valid_svg(self):
        result = self.engine.run({
            "module_data": {"modules": [{"name": "Module A"}, {"name": "Module B"}]},
            "tech_stack_data": {},
            "timeline_data": {},
        })
        svg = result["workflow_svg"]
        assert svg.startswith("<?xml")
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "Module A" in svg
        assert "Module B" in svg

    def test_timeline_svg_is_valid_svg(self):
        result = self.engine.run({
            "module_data": {},
            "tech_stack_data": {},
            "timeline_data": {
                "phases": [
                    {"name": "Discovery", "duration_weeks": 2},
                    {"name": "Build", "duration_weeks": 4},
                ]
            },
        })
        svg = result["timeline_svg"]
        assert svg.startswith("<?xml")
        assert "<svg" in svg
        assert "</svg>" in svg
        assert "Discovery" in svg
        assert "Build" in svg
        assert "W0" in svg

    def test_architecture_svg_is_valid_svg(self):
        result = self.engine.run({
            "module_data": {},
            "tech_stack_data": {"frontend": ["React"], "backend": ["FastAPI"]},
            "timeline_data": {},
        })
        svg = result["architecture_svg"]
        assert svg.startswith("<?xml")
        assert "<svg" in svg
        assert "</svg>" in svg

    def test_empty_modules_generates_default(self):
        result = self.engine.run({
            "module_data": {"modules": []},
            "tech_stack_data": {},
            "timeline_data": {},
        })
        assert "User Portal" in result["workflow_svg"]

    def test_mermaid_workflow_generated(self):
        result = self.engine.run({
            "module_data": {"modules": [{"name": "Auth"}, {"name": "Payments"}]},
            "tech_stack_data": {},
            "timeline_data": {},
        })
        assert result["mermaid_workflow"].startswith("flowchart LR")
        assert "Auth" in result["mermaid_workflow"]
        assert "Payments" in result["mermaid_workflow"]

    def test_mermaid_timeline_generated(self):
        result = self.engine.run({
            "module_data": {},
            "tech_stack_data": {},
            "timeline_data": {
                "phases": [
                    {"phase": 1, "name": "Plan", "duration_weeks": 2},
                    {"phase": 2, "name": "Build", "duration_weeks": 4},
                ]
            },
        })
        assert result["mermaid_timeline"].startswith("gantt")
        assert "Plan" in result["mermaid_timeline"]
        assert "Build" in result["mermaid_timeline"]
