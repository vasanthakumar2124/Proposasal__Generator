from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.config.constants import ProposalStatus


class ProposalCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    workspace_id: Optional[str] = None


class ProposalUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    status: Optional[ProposalStatus] = None


class ProposalSectionUpdateRequest(BaseModel):
    section_name: str
    content: dict


class ProposalResponse(BaseModel):
    id: str = Field(alias="_id")
    organization_id: str
    project_id: Optional[str]
    client_id: Optional[str]
    workspace_id: Optional[str]
    version: int
    status: ProposalStatus
    title: str
    sections: dict
    ai_generated: bool
    generation_metadata: dict
    created_by: str
    approved_by: Optional[str]
    created_at: datetime
    updated_at: datetime
    proposal_id: Optional[str] = None
    company_name: Optional[str] = None

    model_config = {"populate_by_name": True, "from_attributes": True}
