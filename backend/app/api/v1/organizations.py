from fastapi import APIRouter, Depends, HTTPException

from app.schemas.organization import OrganizationResponse, OrganizationUpdateRequest
from app.schemas.common import MessageResponse
from app.services.organization_service import OrganizationService
from app.infrastructure.di.container import get_service
from app.middleware.tenant_context import TenantContext, get_tenant_context, ensure_tenant_access

router = APIRouter()


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    ctx: TenantContext = Depends(get_tenant_context("settings:read")),
    org_service: OrganizationService = Depends(get_service(OrganizationService)),
):
    if org_id != ctx.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    org = await org_service.get_organization(org_id)
    return OrganizationResponse(
        _id=org.id,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        features=org.features,
        branding=org.branding,
        settings=org.settings,
        status=org.status,
        created_at=org.created_at,
        updated_at=org.updated_at,
    )


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    body: OrganizationUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context("settings:update")),
    org_service: OrganizationService = Depends(get_service(OrganizationService)),
):
    if org_id != ctx.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    org = await org_service.update_organization(
        org_id=org_id,
        name=body.name,
        branding=body.branding.model_dump() if body.branding else None,
        settings=body.settings,
    )
    return OrganizationResponse(
        _id=org.id,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        features=org.features,
        branding=org.branding,
        settings=org.settings,
        status=org.status,
        created_at=org.created_at,
        updated_at=org.updated_at,
    )
