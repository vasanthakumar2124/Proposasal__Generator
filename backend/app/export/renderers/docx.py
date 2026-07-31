import logging
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.export.renderers.base import BaseRenderer

logger = logging.getLogger("proposalcraft.export.docx")


class DOCXRenderer(BaseRenderer):
    extension = ".docx"

    def render(self, proposal: dict, output_path: str) -> str:
        doc = Document()
        style = doc.styles["Normal"]
        style.font.name = "Calibri"
        style.font.size = Pt(10)

        self._add_cover(doc, proposal.get("metadata", {}))

        sections = [
            ("Executive Summary", "executive_summary"),
            ("Proposed Solution", "proposed_solution"),
            ("Modules", "module_breakdown"),
            ("Technology Stack", "technology_stack"),
            ("Timeline", "timeline"),
            ("Investment", "pricing"),
            ("Support", "support"),
            ("Team", "team"),
        ]

        for title, key in sections:
            data = proposal.get(key)
            if data:
                doc.add_page_break()
                self._add_section(doc, title, data)

        path = Path(output_path).with_suffix(".docx")
        doc.save(str(path))
        logger.info("DOCX exported to %s", path)
        return str(path)

    def _add_cover(self, doc: Document, meta: dict):
        for _ in range(6):
            doc.add_paragraph("")

        title = doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title.add_run(meta.get("proposal_title", "Proposal"))
        run.font.size = Pt(28)
        run.font.color.rgb = RGBColor(26, 86, 219)
        run.bold = True

        subtitle = meta.get("subtitle")
        if subtitle:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(subtitle)
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(100, 100, 100)

        doc.add_paragraph("")
        for label, key in [("Prepared for", "prepared_for"), ("Prepared by", "prepared_by"),
                           ("Date", "date"), ("Version", "version")]:
            val = meta.get(key)
            if val:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(f"{label}: {val}")
                run.font.size = Pt(11)

    def _add_section(self, doc: Document, title: str, data: dict | list):
        heading = doc.add_heading(title, level=1)
        for run in heading.runs:
            run.font.color.rgb = RGBColor(26, 86, 219)

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    name = item.get("name", item.get("role", str(item)))
                    desc = item.get("description", item.get("experience", ""))
                    p = doc.add_paragraph(f"• {name}" + (f": {desc}" if desc else ""), style="List Bullet")
                else:
                    doc.add_paragraph(f"• {item}", style="List Bullet")
        elif isinstance(data, dict):
            for key, val in data.items():
                if val:
                    if isinstance(val, list):
                        p = doc.add_paragraph()
                        run = p.add_run(f"{key.replace('_', ' ').title()}: ")
                        run.bold = True
                        items = []
                        for item in val:
                            if isinstance(item, dict):
                                items.append(item.get("name", item.get("module_name", str(item))))
                            else:
                                items.append(str(item))
                        p.add_run(", ".join(items))
                    elif isinstance(val, dict):
                        p = doc.add_paragraph()
                        run = p.add_run(f"{key.replace('_', ' ').title()}: ")
                        run.bold = True
                        p.add_run(str(val))
                    else:
                        p = doc.add_paragraph()
                        run = p.add_run(f"{key.replace('_', ' ').title()}: ")
                        run.bold = True
                        p.add_run(str(val))
