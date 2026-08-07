import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional

logger = logging.getLogger("proposalcraft.proposals_router")

from app.schemas.proposal import ProposalCreateRequest, ProposalUpdateRequest, ProposalResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.proposal_service import ProposalService
from app.services.generated_proposal_service import GeneratedProposalService
from app.export.service import export_service
from app.export.normalize import normalize_proposal
from app.infrastructure.di.container import get_service
from app.middleware.tenant_context import TenantContext, get_tenant_context, ensure_tenant_access
from app.workers.tasks import generate_proposal_task
from app.billing.limits import enforce_proposal_limit

router = APIRouter()


@router.post("", response_model=ProposalResponse, status_code=201)
async def create_proposal(
    body: ProposalCreateRequest,
    ctx: TenantContext = Depends(get_tenant_context("proposal:create")),
    svc: ProposalService = Depends(get_service(ProposalService)),
):
    proposal = await svc.create_proposal(body.model_dump(exclude_unset=True), ctx.organization_id, ctx.user.id)
    return ProposalResponse(**proposal.model_dump(by_alias=True))


@router.get("", response_model=PaginatedResponse[ProposalResponse])
async def list_proposals(
    skip: int = 0, limit: int = 100,
    status: Optional[str] = Query(None),
    ctx: TenantContext = Depends(get_tenant_context("proposal:read")),
    svc: ProposalService = Depends(get_service(ProposalService)),
):
    proposals = await svc.list_proposals(ctx.organization_id, skip=skip, limit=limit, status=status)
    items = [ProposalResponse(**p.model_dump(by_alias=True)) for p in proposals]
    return PaginatedResponse(items=items, total=len(items), skip=skip, limit=limit)


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(
    proposal_id: str,
    ctx: TenantContext = Depends(get_tenant_context("proposal:read")),
    svc: ProposalService = Depends(get_service(ProposalService)),
    gen_svc: GeneratedProposalService = Depends(get_service(GeneratedProposalService)),
):
    try:
        proposal = await svc.get_proposal(proposal_id)
        ensure_tenant_access(proposal, ctx)
        return ProposalResponse(**proposal.model_dump(by_alias=True))
    except Exception:
        gen = await gen_svc.get_proposal(proposal_id)
        if not gen or gen.get("organization_id") != ctx.user.organization_id:
            raise HTTPException(status_code=404, detail="Proposal not found")
        error = gen.get("error")
        gen_meta = gen.get("generation_metadata") or {}
        if error:
            gen_meta["error"] = error
        return ProposalResponse(
            _id=gen["_id"],
            title=gen.get("title", "Untitled"),
            organization_id=gen.get("organization_id", ""),
            created_by=gen.get("created_by", ""),
            status=gen.get("status", "draft"),
            sections=gen.get("sections", {}),
            project_id=gen.get("project_id"),
            client_id=gen.get("client_id"),
            workspace_id=gen.get("workspace_id"),
            version=gen.get("version", 1),
            ai_generated=gen.get("ai_generated", False),
            generation_metadata=gen_meta,
            approved_by=gen.get("approved_by"),
            created_at=gen.get("created_at"),
            updated_at=gen.get("updated_at"),
            proposal_id=gen.get("proposal_id"),
            company_name=gen.get("company_name"),
        )


@router.put("/{proposal_id}", response_model=ProposalResponse)
async def update_proposal(
    proposal_id: str, body: ProposalUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context("proposal:update")),
    svc: ProposalService = Depends(get_service(ProposalService)),
):
    try:
        proposal = await svc.update_proposal(proposal_id, body.model_dump(exclude_unset=True))
        ensure_tenant_access(proposal, ctx)
        return ProposalResponse(**proposal.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{proposal_id}", response_model=MessageResponse)
async def delete_proposal(
    proposal_id: str,
    ctx: TenantContext = Depends(get_tenant_context("proposal:delete")),
    svc: ProposalService = Depends(get_service(ProposalService)),
):
    try:
        proposal = await svc.get_proposal(proposal_id)
        ensure_tenant_access(proposal, ctx)
        await svc.delete_proposal(proposal_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MessageResponse(message="Proposal archived")


@router.get("/{proposal_id}/export/{fmt}")
async def export_proposal(
    proposal_id: str,
    fmt: str,
    ctx: TenantContext = Depends(get_tenant_context("proposal:read")),
    gen_svc: GeneratedProposalService = Depends(get_service(GeneratedProposalService)),
):
    if fmt not in ("html", "pdf", "docx", "pptx"):
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")

    gen = await gen_svc.get_proposal(proposal_id)
    if not gen or gen.get("organization_id") != ctx.user.organization_id:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Normalize generated proposal for export renderers
    normalize_proposal(gen)

    try:
        path = export_service.export(gen, fmt)
        media_types = {
            "html": "text/html",
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        }
        return FileResponse(
            path=path,
            media_type=media_types.get(fmt, "application/octet-stream"),
            filename=Path(path).name,
        )
    except Exception as e:
        logger.error("Export failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=dict)
async def generate_proposal(
    body: dict,
    ctx: TenantContext = Depends(get_tenant_context("proposal:create")),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    svc: GeneratedProposalService = Depends(get_service(GeneratedProposalService)),
):
    org_id = ctx.organization_id
    await enforce_proposal_limit(org_id)
    doc = await svc.start_generation(
        client_input=body.get("client_input", ""),
        domain=body.get("domain"),
        project_type=body.get("project_type"),
        org_id=org_id,
        user_id=ctx.user.id,
    )
    try:
        generate_proposal_task.delay(
            doc["_id"],
            body.get("client_input", ""),
            org_id,
            ctx.user.id,
            body.get("domain"),
            body.get("project_type"),
        )
        logger.info("Proposal %s enqueued to celery", doc["_id"])
    except Exception as e:
        logger.warning("Celery enqueue failed, falling back to in-process task: %s", e)
        background_tasks.add_task(
            svc.run_and_finalize,
            doc["_id"],
            body.get("client_input", ""),
            org_id,
            ctx.user.id,
            body.get("domain"),
            body.get("project_type"),
        )
    return doc


@router.put("/{proposal_id}/sections/{section_name}", response_model=ProposalResponse)
async def update_section(
    proposal_id: str, section_name: str, body: dict,
    ctx: TenantContext = Depends(get_tenant_context("proposal:update")),
    svc: ProposalService = Depends(get_service(ProposalService)),
):
    try:
        proposal = await svc.update_section(proposal_id, section_name, body)
        ensure_tenant_access(proposal, ctx)
        return ProposalResponse(**proposal.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
