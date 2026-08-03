import logging
import tempfile
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from app.config.settings import settings
from app.export.renderers.base import BaseRenderer
from app.export.renderers.common import (
    SECTION_LABELS as TOC_LABELS,
    RENDERED_SECTION_KEYS,
    DIAGRAM_SECTION_KEYS,
    section_order_from_rules,
)

logger = logging.getLogger("proposalcraft.export.html_renderer")

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates" / "pdf"

NON_TOC_SECTIONS = {"cover_page", "table_of_contents"}

TOC_RENDERED_SECTIONS = {
    "about_company", "executive_summary", "client_understanding", "requirement_analysis",
    "proposed_solution", "module_breakdown", "user_journey", "technology_stack",
    "diagrams", "timeline", "pricing", "custom_development_charges", "sla", "support",
    "terms", "deliverables", "security", "methodology", "case_studies", "team", "conclusion",
}


class HTMLPDFRenderer(BaseRenderer):
    extension = ".pdf"

    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    def _prepare_context(self, proposal: dict) -> dict:
        sections = proposal.get("sections", proposal)
        metadata = proposal.get("metadata", proposal.get("proposal_metadata", {}))

        section_order = section_order_from_rules()
        include_diagrams = settings.ENABLE_DIAGRAMS_APPENDIX

        def _has_section(key: str) -> bool:
            if key == "diagrams":
                return include_diagrams and any(sections.get(dk) for dk in DIAGRAM_SECTION_KEYS)
            return bool(sections.get(key))

        toc_entries = [
            {"key": s, "label": TOC_LABELS.get(s, s.replace("_", " ").title())}
            for s in section_order
            if s not in NON_TOC_SECTIONS
            and s in TOC_RENDERED_SECTIONS
            and _has_section(s)
        ]

        css_path = TEMPLATE_DIR / "proposal.css"
        css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

        return {
            "css": css,
            "metadata": metadata,
            "toc_entries": toc_entries,
            "section_order": section_order,
            "include_diagrams_appendix": include_diagrams,
            **{k: v for k, v in sections.items() if k not in ("css", "metadata", "toc_entries", "section_order")},
        }

    def render(self, proposal: dict, output_path: str) -> str:
        context = self._prepare_context(proposal)

        template = self.env.get_template("proposal.html")
        html = template.render(**context)

        path = Path(output_path).with_suffix(".pdf")
        pdf_bytes = self._html_to_pdf(html)
        path.write_bytes(pdf_bytes)
        logger.info("PDF rendered via HTML+WeasyPrint to %s", path)
        return str(path)

    def render_html(self, proposal: dict) -> str:
        context = self._prepare_context(proposal)

        template = self.env.get_template("proposal.html")
        return template.render(**context)

    def _html_to_pdf(self, html: str) -> bytes:
        try:
            from weasyprint import HTML
            return HTML(string=html).write_pdf(None)
        except OSError as e:
            if "libgobject" in str(e) or "libpango" in str(e) or "libcairo" in str(e):
                raise RuntimeError(
                    "PDF export requires GTK system libraries. "
                    "On Linux they are installed in the Docker container. "
                    "On Windows, install GTK from: "
                    "https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer"
                ) from e
            raise


html_pdf_renderer = HTMLPDFRenderer()
