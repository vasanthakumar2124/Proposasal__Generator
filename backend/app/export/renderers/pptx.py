import logging
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from app.export.renderers.base import BaseRenderer

logger = logging.getLogger("proposalcraft.export.pptx")

BLUE = RGBColor(26, 86, 219)
DARK = RGBColor(51, 51, 51)
GRAY = RGBColor(100, 100, 100)


class PPTXRenderer(BaseRenderer):
    extension = ".pptx"

    def render(self, proposal: dict, output_path: str) -> str:
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        self._add_cover_slide(prs, proposal.get("metadata", {}))

        sections = [
            ("Executive Summary", "executive_summary"),
            ("Proposed Solution", "proposed_solution"),
            ("Modules", "module_breakdown"),
            ("Technology Stack", "technology_stack"),
            ("Timeline", "timeline"),
            ("Investment", "pricing"),
            ("Team", "team"),
        ]

        for title, key in sections:
            data = proposal.get(key)
            if data:
                self._add_section_slide(prs, title, data)

        path = Path(output_path).with_suffix(".pptx")
        prs.save(str(path))
        logger.info("PPTX exported to %s", path)
        return str(path)

    def _add_cover_slide(self, prs: Presentation, meta: dict):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = RGBColor(240, 244, 255)

        txBox = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(3))
        tf = txBox.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = meta.get("proposal_title", "Proposal")
        p.font.size = Pt(40)
        p.font.color.rgb = BLUE
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER

        subtitle = meta.get("subtitle", "")
        if subtitle:
            p2 = tf.add_paragraph()
            p2.text = subtitle
            p2.font.size = Pt(20)
            p2.font.color.rgb = GRAY
            p2.alignment = PP_ALIGN.CENTER

        p3 = tf.add_paragraph()
        p3.text = ""
        p3.space_before = Pt(20)
        for label, key in [("Prepared for", "prepared_for"), ("Date", "date")]:
            val = meta.get(key)
            if val:
                p4 = tf.add_paragraph()
                p4.text = f"{label}: {val}"
                p4.font.size = Pt(14)
                p4.font.color.rgb = DARK
                p4.alignment = PP_ALIGN.CENTER

    def _add_section_slide(self, prs: Presentation, title: str, data: dict | list):
        slide = prs.slides.add_slide(prs.slide_layouts[6])

        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(1))
        tf = txBox.text_frame
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(32)
        p.font.color.rgb = BLUE
        p.font.bold = True

        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.3), Inches(12), Inches(5.5))
        ctf = content_box.text_frame
        ctf.word_wrap = True

        if isinstance(data, list):
            for item in data:
                p = ctf.add_paragraph()
                if isinstance(item, dict):
                    name = item.get("name", item.get("role", str(item)))
                    desc = item.get("description", item.get("experience", ""))
                    p.text = f"• {name}" + (f": {desc}" if desc else "")
                else:
                    p.text = f"• {item}"
                p.font.size = Pt(16)
                p.font.color.rgb = DARK
                p.space_after = Pt(4)
        elif isinstance(data, dict):
            for key, val in data.items():
                if val:
                    p = ctf.add_paragraph()
                    if isinstance(val, list):
                        items = []
                        for item in val:
                            if isinstance(item, dict):
                                items.append(item.get("name", item.get("module_name", str(item))))
                            else:
                                items.append(str(item))
                        p.text = f"{key.replace('_', ' ').title()}: {', '.join(items)}"
                    elif isinstance(val, dict):
                        p.text = f"{key.replace('_', ' ').title()}: {str(val)}"
                    else:
                        p.text = f"{key.replace('_', ' ').title()}: {val}"
                    p.font.size = Pt(16)
                    p.font.color.rgb = DARK
                    p.space_after = Pt(4)

        if ctf.paragraphs[0].text == "":
            ctf.paragraphs[0].text = title
            ctf.paragraphs[0].font.size = Pt(24)
