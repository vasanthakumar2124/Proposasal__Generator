from typing import TypedDict, Optional


class ProposalState(TypedDict):

    # User Input
    requirement: str

    # Requirement Agent Output
    requirement_json: Optional[dict]

    # RAG Agent Output
    rag_context: Optional[dict]

    # Feature Agent Output
    features: Optional[dict]

    business_analysis: dict

    # Proposal Writer Output
    proposal: Optional[dict]

    # PDF Generator Output
    pdf_path: Optional[str]
    pdf_file:str