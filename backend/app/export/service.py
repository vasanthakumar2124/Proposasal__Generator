import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.export.renderers.html import HTMLRenderer
from app.export.renderers.docx import DOCXRenderer
from app.export.renderers.pptx import PPTXRenderer
from app.export.renderers.html_renderer import html_pdf_renderer

logger = logging.getLogger("proposalcraft.export.service")

EXPORT_DIR = Path(tempfile.gettempdir()) / "proposalcraft_exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

RENDERERS = {
    "html": HTMLRenderer(),
    "pdf": html_pdf_renderer,
    "docx": DOCXRenderer(),
    "pptx": PPTXRenderer(),
}


class ExportService:
    def __init__(self):
        self.renderers = RENDERERS

    def export(self, proposal: dict, fmt: str, output_path: Optional[str] = None) -> str:
        fmt = fmt.lower()
        if fmt not in self.renderers:
            raise ValueError(f"Unsupported format: {fmt}. Supported: {list(self.renderers.keys())}")

        renderer = self.renderers[fmt]
        if not output_path:
            title = proposal.get("metadata", {}).get("proposal_title", "proposal")
            safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title}_{timestamp}{renderer.extension}"
            output_path = str(EXPORT_DIR / filename)

        result = renderer.render(proposal, output_path)
        logger.info("Exported proposal to %s", result)
        return result

    def export_all(self, proposal: dict) -> dict[str, str]:
        results = {}
        for fmt in self.renderers:
            try:
                results[fmt] = self.export(proposal, fmt)
            except Exception as e:
                logger.error("Failed to export %s: %s", fmt, e)
                results[fmt] = str(e)
        return results


export_service = ExportService()
