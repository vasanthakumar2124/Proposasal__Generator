from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.config.constants import ProposalStatus


class Proposal(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v) if v is not None else v
    organization_id: str
    project_id: Optional[str] = None
    client_id: Optional[str] = None
    workspace_id: Optional[str] = None
    version: int = 1
    status: ProposalStatus = ProposalStatus.DRAFT
    title: str
    sections: dict = Field(default_factory=dict)
    ai_generated: bool = False
    generation_metadata: dict = Field(default_factory=dict)
    created_by: str
    approved_by: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}
