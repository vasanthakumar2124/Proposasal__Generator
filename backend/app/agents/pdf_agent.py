import tempfile
from pathlib import Path

from app.export.renderers.html_renderer import html_pdf_renderer


class PDFAgent:
    def __init__(self):
        self.name = "PDF Generator Agent"

    def run(self, proposal_data: dict, output_path: str = "") -> dict:
        if not output_path:
            output_path = str(Path(tempfile.gettempdir()) / "generated_proposal.pdf")
        result_path = html_pdf_renderer.render(proposal_data, output_path)
        return {"pdf_file": result_path}
