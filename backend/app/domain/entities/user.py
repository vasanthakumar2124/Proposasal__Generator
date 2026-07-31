from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator

from app.config.constants import UserRole


class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return str(v) if v is not None else v
    email: EmailStr
    password_hash: str
    name: str
    organization_id: str
    role: UserRole = UserRole.EDITOR
    permissions: list[str] = Field(default_factory=list)
    auth_provider: str = "email"
    auth_provider_id: str = ""
    avatar_url: str = ""
    status: str = "active"
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"populate_by_name": True, "arbitrary_types_allowed": True}

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def update_login(self) -> None:
        self.last_login = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
