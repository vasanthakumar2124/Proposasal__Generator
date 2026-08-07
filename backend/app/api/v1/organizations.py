from fastapi import APIRouter, Depends, HTTPException

from app.domain.entities.user import User
from app.schemas.organization import OrganizationResponse, OrganizationUpdateRequest
from app.schemas.common import MessageResponse
from app.services.organization_service import OrganizationService
from app.api.deps import get_current_user, get_current_org, require_permission
from app.infrastructure.di.container import get_service

router = APIRouter()


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    current_org_id: str = Depends(get_current_org),
    user: User = Depends(require_permission("settings:read")),
    org_service: OrganizationService = Depends(get_service(OrganizationService)),
):
    if org_id != current_org_id:
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
    current_org_id: str = Depends(get_current_org),
    user: User = Depends(require_permission("settings:update")),
    org_service: OrganizationService = Depends(get_service(OrganizationService)),
):
    if org_id != current_org_id:
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
