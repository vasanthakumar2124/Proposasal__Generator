from typing import TypedDict, Optional, Any


class ProposalState(TypedDict):
    raw_client_input: str
    requirements: Optional[dict]
    rag_context: Optional[dict]
    business_context: Optional[dict]
    proposal_draft: Optional[dict]
    review: Optional[dict]
    final_proposal: Optional[dict]
    rubric_result: Optional[dict]
    rubric_issues: Optional[list]
    rubric_retries: Optional[int]
    error: Optional[str]
