"""Print-preview regression: with .section page-break-inside:auto, short
sections flow instead of jumping whole to the next page, so no interior page
should be less than ~60% full (last page, cover, and TOC excepted)."""

import os

import pytest


def _build_short_section_proposal() -> dict:
    """Proposal whose About Us has only 2 short fields filled — the case that
    used to force the whole section onto its own page."""
    para = (
        "The operations team currently manages orders through spreadsheets and email, "
        "which causes duplicate entries, delayed handoffs, and no visibility into "
        "daily volumes. This proposal replaces that process with a purpose-built "
        "portal that tracks every order from intake through delivery."
    )
    return {
        "metadata": {
            "proposal_title": "Density Check",
            "company_name": "Acme Software",
            "client_name": "Sample Client",
            "date": "2026-01-01",
            "version": "1.0",
            "proposal_id": "PROP-0001",
        },
        "about_company": {
            "who_we_are": "We are a focused delivery team. We ship software. Small.",
            "experience": "We have done similar work before.",
        },
        "executive_summary": {
            "business_overview": para,
            "problem_statement": para,
            "proposed_solution": para,
            "expected_roi": para,
            "business_value": para,
            "key_benefits": [
                "Orders move through the system in one place instead of email threads.",
                "Every handoff is logged, so nothing gets lost between teams.",
                "Daily volumes become visible to management in real time.",
            ],
        },
        "client_understanding": {
            "business_overview": para,
            "current_challenges": [para, para],
            "pain_points": [para, para],
            "business_goals": [para, para],
            "opportunities": [para],
        },
        "proposed_solution": {
            "overview": para,
            "architecture": para,
            "workflow": para,
            "security": para,
            "scalability": para,
        },
        "module_breakdown": {
            "standard_modules": [
                {"module_name": f"Module {i}", "description": "Handles intake, tracking, and reporting for orders."}
                for i in range(6)
            ],
            "custom_modules": [],
        },
        "technology_stack": {
            "frontend": ["React 19", "TypeScript"],
            "backend": ["FastAPI", "PostgreSQL"],
            "deployment": ["Docker", "AWS"],
            "rationale": "The stack matches the team's existing skills and the portal's workload.",
        },
        "conclusion": {
            "summary": "This proposal lays out a clear path to replace manual order handling with a tracked portal.",
            "next_steps": ["Review scope", "Approve budget", "Kick off discovery"],
        },
    }


class TestPrintPreviewDensity:
    def test_no_interior_page_below_60_percent_fill(self):
        try:
            from weasyprint import HTML  # noqa: F401
        except OSError:
            pytest.skip("WeasyPrint native dependencies not available")

        import fitz

        from app.export import export_service

        path = export_service.export(_build_short_section_proposal(), "pdf")
        assert path.endswith(".pdf")
        assert os.path.getsize(path) > 0

        doc = fitz.open(path)
        try:
            n = len(doc)
            assert n >= 4, f"expected cover+TOC+content pages, got {n}"
            # pages[0] cover, pages[1] TOC, last page exempt by design
            interior = list(range(2, n - 1))
            for pno in interior:
                fill = _content_fill(doc[pno])
                assert fill >= 0.6, (
                    f"page {pno + 1} only {fill:.0%} full — short sections are not flowing"
                )
        finally:
            doc.close()


def _content_fill(page) -> float:
    """Fraction of the usable A4 area (below top margin, above bottom margin)
    covered by rendered content blocks. Excludes running header/footer."""
    usable = 297 * 72 / 25.4 - 2 * 20 * 72 / 25.4
    spans = [(b[1], b[3]) for b in page.get_text("blocks") if b[3] > 45 and b[1] < usable]
    if not spans:
        return 0.0
    top = min(y0 for y0, _ in spans)
    bottom = max(y1 for _, y1 in spans)
    return (bottom - top) / usable
