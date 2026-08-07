import logging

from fastapi import APIRouter, Depends

from app.analytics.service import analytics_service
from app.domain.entities.user import User
from app.api.deps import require_permission
from app.middleware.tenant_context import TenantContext, get_tenant_context

logger = logging.getLogger("proposalcraft.analytics.router")

router = APIRouter()


@router.get("/dashboard")
async def get_org_dashboard(
    ctx: TenantContext = Depends(get_tenant_context("proposal:read")),
):
    return await analytics_service.get_org_dashboard(ctx.organization_id)


@router.get("/admin/dashboard")
async def get_admin_dashboard(
    user: User = Depends(require_permission("admin")),
):
    return await analytics_service.get_admin_dashboard()
