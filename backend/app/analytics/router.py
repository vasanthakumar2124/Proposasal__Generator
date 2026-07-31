import logging

from fastapi import APIRouter, Depends

from app.analytics.service import analytics_service
from app.domain.entities.user import User
from app.api.deps import get_current_user, get_current_org, require_permission

logger = logging.getLogger("proposalcraft.analytics.router")

router = APIRouter()


@router.get("/dashboard")
async def get_org_dashboard(
    user: User = Depends(require_permission("proposal:read")),
    org_id: str = Depends(get_current_org),
):
    return await analytics_service.get_org_dashboard(org_id)


@router.get("/admin/dashboard")
async def get_admin_dashboard(
    user: User = Depends(require_permission("admin")),
):
    return await analytics_service.get_admin_dashboard()
