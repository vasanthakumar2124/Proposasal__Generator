import pytest


class TestExportServicePDF:
    def test_pdf_renderer_is_html_pdf_renderer(self):
        from app.export.service import RENDERERS
        renderer = RENDERERS["pdf"]
        assert renderer.extension == ".pdf"
        assert hasattr(renderer, "_html_to_pdf") or hasattr(renderer, "render_html")

    def test_pdf_export_does_not_crash(self):
        try:
            from weasyprint import HTML  # noqa: F401
        except OSError:
            pytest.skip("WeasyPrint native dependencies not available")
        from app.export import export_service
        proposal = {
            "metadata": {"proposal_title": "TestPDF"},
            "executive_summary": {"business_overview": "test"},
        }
        path = export_service.export(proposal, "pdf")
        assert path.endswith(".pdf")
        import os
        assert os.path.getsize(path) > 0
