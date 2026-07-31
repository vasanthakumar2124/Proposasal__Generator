import pytest


SAMPLE_PROPOSAL = {
    "metadata": {
        "proposal_title": "Test Proposal",
        "prepared_for": "Acme Corp",
        "prepared_by": "ProposalCraft",
        "date": "2024-01-01",
        "version": "1.0",
    },
    "executive_summary": {
        "business_overview": "Test overview",
        "problem_statement": "Test problem",
        "key_benefits": ["Speed", "Quality"],
    },
    "proposed_solution": {
        "overview": "Solution description",
        "architecture": "Microservices with event-driven design",
    },
    "module_breakdown": [
        {"name": "Auth Module", "description": "Authentication system"},
        {"name": "Payment Module", "description": "Payment processing"},
    ],
    "technology_stack": {
        "frontend": ["React", "TypeScript"],
        "backend": ["Python", "FastAPI"],
        "database": ["PostgreSQL"],
    },
    "timeline": {
        "milestones": ["Design phase", "Development phase", "Deployment"],
    },
    "pricing": {
        "development_cost": "$50,000",
        "payment_terms": "Net 30",
    },
    "support": {
        "basic": "Email support",
        "standard": "24/7 support",
    },
    "sla": {
        "critical": "1 hour",
        "high": "4 hours",
    },
    "team": [
        {"name": "Alice", "role": "PM", "experience": "10 years"},
        {"name": "Bob", "role": "Developer", "experience": "5 years"},
    ],
    "conclusion": {
        "summary": "We look forward to working with you.",
    },
}


class TestExportService:
    def test_export_html(self):
        from app.export import export_service
        path = export_service.export(SAMPLE_PROPOSAL, "html")
        assert path.endswith(".html")
        import os
        assert os.path.getsize(path) > 100

    def test_export_pdf(self):
        try:
            from weasyprint import HTML
        except Exception:
            pytest.skip("WeasyPrint native dependencies not available")
        from app.export import export_service
        path = export_service.export(SAMPLE_PROPOSAL, "pdf")
        assert path.endswith(".pdf")
        import os
        assert os.path.getsize(path) > 500

    def test_export_docx(self):
        from app.export import export_service
        path = export_service.export(SAMPLE_PROPOSAL, "docx")
        assert path.endswith(".docx")
        import os
        assert os.path.getsize(path) > 500

    def test_export_pptx(self):
        from app.export import export_service
        path = export_service.export(SAMPLE_PROPOSAL, "pptx")
        assert path.endswith(".pptx")
        import os
        assert os.path.getsize(path) > 500

    def test_export_all(self):
        from app.export import export_service
        results = export_service.export_all(SAMPLE_PROPOSAL)
        assert "html" in results
        assert "pdf" in results
        assert "docx" in results
        assert "pptx" in results

    def test_export_invalid_format(self):
        from app.export import export_service
        with pytest.raises(ValueError, match="Unsupported format"):
            export_service.export(SAMPLE_PROPOSAL, "txt")
