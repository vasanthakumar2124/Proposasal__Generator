from dataclasses import dataclass

from fastapi import Depends, HTTPException

from app.domain.entities.user import User
from app.api.deps import require_permission


@dataclass(frozen=True)
class TenantContext:
    """Request-scoped tenant identity: user + their organization id.

    Resolved once per request by get_tenant_context(permission), which
    replaces the previous `require_permission(...)` + `get_current_org`
    dependency chains in every handler."""

    user: User
    organization_id: str

    def has_permission(self, permission: str) -> bool:
        return self.user.has_permission(permission)

    def ensure_owner(self, entity) -> None:
        if getattr(entity, "organization_id", None) != self.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")


def get_tenant_context(permission: str):
    async def _tenant_context(
        user: User = Depends(require_permission(permission)),
    ) -> TenantContext:
        return TenantContext(user=user, organization_id=user.organization_id)

    return _tenant_context


def ensure_tenant_access(entity, ctx: TenantContext) -> None:
    ctx.ensure_owner(entity)
