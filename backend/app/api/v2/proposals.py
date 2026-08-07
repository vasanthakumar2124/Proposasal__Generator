from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.domain.exceptions import InvalidStateTransitionError
from app.infrastructure.di.container import get_service
from app.middleware.tenant_context import TenantContext, ensure_tenant_access, get_tenant_context
from app.services.proposal_service import ProposalService
from app.services.proposal_version_service import ProposalVersionService

router = APIRouter()


class StatusTransitionRequest(BaseModel):
    target: str = Field(..., min_length=1)


@router.post("/{proposal_id}/status")
async def change_proposal_status(
    proposal_id: str,
    body: StatusTransitionRequest,
    ctx: TenantContext = Depends(get_tenant_context("proposal:update")),
    svc: ProposalService = Depends(get_service(ProposalService)),
):
    """Advance a proposal through the lifecycle state machine."""
    try:
        proposal = await svc.get_proposal(proposal_id)
        ensure_tenant_access(proposal, ctx)
        updated = await svc.transition_status(proposal_id, body.target, ctx.user.id)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return {"_id": proposal_id, "status": updated.status}


@router.get("/{proposal_id}/versions")
async def list_proposal_versions(
    proposal_id: str,
    ctx: TenantContext = Depends(get_tenant_context("proposal:read")),
    version_svc: ProposalVersionService = Depends(get_service(ProposalVersionService)),
):
    try:
        return {"proposal_id": proposal_id, "versions": await version_svc.list_versions(proposal_id, ctx.organization_id)}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{proposal_id}/versions/diff")
async def diff_proposal_versions(
    proposal_id: str,
    from_version: str = Query(...),
    to_version: str = Query(...),
    ctx: TenantContext = Depends(get_tenant_context("proposal:read")),
    version_svc: ProposalVersionService = Depends(get_service(ProposalVersionService)),
):
    try:
        return await version_svc.diff_versions(proposal_id, from_version, to_version, ctx.organization_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{proposal_id}/versions/{version_id}/restore")
async def restore_proposal_version(
    proposal_id: str,
    version_id: str,
    ctx: TenantContext = Depends(get_tenant_context("proposal:update")),
    version_svc: ProposalVersionService = Depends(get_service(ProposalVersionService)),
):
    try:
        return await version_svc.restore_version(proposal_id, version_id, ctx.organization_id, ctx.user.id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{proposal_id}/versions/latest")
async def latest_proposal_version(
    proposal_id: str,
    ctx: TenantContext = Depends(get_tenant_context("proposal:read")),
    version_svc: ProposalVersionService = Depends(get_service(ProposalVersionService)),
):
    """Alias: returns the most recent snapshot (version list head)."""
    try:
        versions = await version_svc.list_versions(proposal_id, ctx.organization_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    if not versions:
        raise HTTPException(status_code=404, detail="No versions found")
    return versions[0]


@router.get("/{proposal_id}/versions/count")
async def count_proposal_versions(
    proposal_id: str,
    ctx: TenantContext = Depends(get_tenant_context("proposal:read")),
    version_svc: ProposalVersionService = Depends(get_service(ProposalVersionService)),
):
    try:
        versions = await version_svc.list_versions(proposal_id, ctx.organization_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"proposal_id": proposal_id, "count": len(versions)}
