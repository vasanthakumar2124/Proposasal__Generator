from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.config.constants import IndustryType


class ProjectCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    industry: IndustryType = IndustryType.CUSTOM
    project_type: str = "custom"
    workspace_id: Optional[str] = None
    client_id: Optional[str] = None


class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    industry: Optional[IndustryType] = None
    project_type: Optional[str] = None
    workspace_id: Optional[str] = None
    client_id: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str = Field(alias="_id")
    organization_id: str
    workspace_id: Optional[str]
    client_id: Optional[str]
    name: str
    description: str
    industry: IndustryType
    project_type: str
    status: str
    proposal_ids: list[str]
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True, "from_attributes": True}
