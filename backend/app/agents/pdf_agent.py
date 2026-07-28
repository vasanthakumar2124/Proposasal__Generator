from app.utils.pdf_generator import create_pdf


class PDFAgent:

    def __init__(self):
        self.name = "PDF Generator Agent"

    def run(
        self,
        proposal_text,
        requirement
    ):

        output_file = "generated/generated_proposal.pdf"

        pdf_path = create_pdf(
            proposal_text=proposal_text,
            output_path=output_file,
            requirement=requirement
        )

        return {
            "pdf_file": pdf_path
        }