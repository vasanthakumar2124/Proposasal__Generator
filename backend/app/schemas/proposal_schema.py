from pydantic import BaseModel


# Existing Schema
class ProposalCreate(BaseModel):
    title: str
    client: str
    status: str


class ProposalRequest(BaseModel):
    requirement: str


class ProposalResponse(BaseModel):
    proposal_id: str
    project_name: str
    generated_date: str
    proposal: str
    pdf_file: str