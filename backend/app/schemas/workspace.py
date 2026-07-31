from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=1000)


class WorkspaceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class WorkspaceResponse(BaseModel):
    id: str = Field(alias="_id")
    organization_id: str
    name: str
    description: str
    created_by: str
    members: list[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"populate_by_name": True, "from_attributes": True}


class AddWorkspaceMemberRequest(BaseModel):
    user_id: str
    role: Optional[str] = "editor"
