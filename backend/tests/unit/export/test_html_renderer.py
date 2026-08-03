import pytest


class TestHTMLPDFRenderer:
    def test_proposal_with_diagrams_renders_without_error(self):
        from app.export.renderers.html_renderer import html_pdf_renderer
        proposal = {
            "metadata": {"proposal_title": "Test"},
            "executive_summary": {"business_overview": "test"},
            "workflow_diagram_svg": "<svg xmlns='http://www.w3.org/2000/svg'><rect/></svg>",
            "timeline_diagram_svg": "<svg xmlns='http://www.w3.org/2000/svg'><circle/></svg>",
        }
        html = html_pdf_renderer.render_html(proposal)
        assert "<svg" in html
        assert "workflow" in html or "Solution Workflow" in html

    def test_proposal_with_writer_keys_renders_html(self):
        from app.export.renderers.html_renderer import html_pdf_renderer
        from app.export.normalize import normalize_proposal
        raw = {
            "metadata": {"proposal_title": "Test"},
            "executive_summary": "Summary text",
            "client_understanding": {
                "business_overview": "bg",
                "objectives": ["o1"],
                "scope": "in",
                "out_of_scope": [],
            },
            "proposed_solution": {
                "architecture": "arch",
                "overview": "solution overview",
            },
            "core_features": [{"name": "F1", "description": "desc", "benefit": "b"}],
            "implementation_plan": {
                "timeline": "8w",
                "milestones": ["m1"],
                "team": "3 devs",
            },
            "why_choose_us": {"expertise": "exp", "approach": "app", "support": "sup"},
            "next_steps": ["Step 1"],
        }
        normalized = normalize_proposal(raw)
        html = html_pdf_renderer.render_html(normalized)
        assert "Summary text" in html
        assert "bg" in html
        assert "arch" in html
        assert "F1" in html
        assert "exp" in html
        assert "Step 1" in html

    def test_render_html_does_not_raise(self):
        from app.export.renderers.html_renderer import html_pdf_renderer
        minimal = {
            "metadata": {"proposal_title": "Minimal"},
            "executive_summary": {"business_overview": "Hello"},
        }
        html = html_pdf_renderer.render_html(minimal)
        assert "Hello" in html
