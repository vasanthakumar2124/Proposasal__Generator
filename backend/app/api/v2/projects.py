import logging

from fastapi import APIRouter, Depends, Header, HTTPException

from app.billing.limits import enforce_proposal_limit
from app.infrastructure.database.mongodb import get_database
from app.infrastructure.di.container import get_service
from app.middleware.tenant_context import TenantContext, ensure_tenant_access, get_tenant_context
from app.schemas.project_v2 import ProjectHubGenerateRequest, ProjectHubUpdateRequest
from app.services.generated_proposal_service import GeneratedProposalService
from app.services.project_service import ProjectService
from app.workers.tasks import generate_proposal_task

logger = logging.getLogger("proposalcraft.projects_v2_router")

router = APIRouter()


@router.get("/{project_id}/hub")
async def get_project_hub(
    project_id: str,
    ctx: TenantContext = Depends(get_tenant_context("project:read")),
    svc: ProjectService = Depends(get_service(ProjectService)),
):
    try:
        project = await svc.get_project(project_id)
        ensure_tenant_access(project, ctx)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    db = await get_database()

    proposals = []
    cursor = db.generated_proposals.find(
        {"organization_id": ctx.organization_id, "project_id": project_id}
    ).sort("created_at", -1).limit(50)
    async for doc in cursor:
        proposals.append(
            {
                "_id": str(doc["_id"]),
                "proposal_id": doc.get("proposal_id"),
                "title": doc.get("title", "Untitled"),
                "status": doc.get("status", "draft"),
                "error": doc.get("error"),
                "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
            }
        )

    activity = []
    cursor = db.activity_events.find(
        {"organization_id": ctx.organization_id, "resource_id": project_id}
    ).sort("occurred_at", -1).limit(20)
    async for ev in cursor:
        ev["_id"] = str(ev["_id"])
        ev["occurred_at"] = ev["occurred_at"].isoformat()
        activity.append(ev)

    return {
        "project": project.model_dump(by_alias=True),
        "proposals": proposals,
        "activity": activity,
    }


@router.patch("/{project_id}")
async def update_project_hub(
    project_id: str,
    body: ProjectHubUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context("project:update")),
    svc: ProjectService = Depends(get_service(ProjectService)),
):
    try:
        existing = await svc.get_project(project_id)
        ensure_tenant_access(existing, ctx)
        project = await svc.update_project(project_id, body.model_dump(exclude_unset=True))
        ensure_tenant_access(project, ctx)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return project.model_dump(by_alias=True)


@router.post("/{project_id}/generate", response_model=dict)
async def generate_for_project(
    project_id: str,
    body: ProjectHubGenerateRequest,
    ctx: TenantContext = Depends(get_tenant_context("proposal:create")),
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    svc: ProjectService = Depends(get_service(ProjectService)),
    gen_svc: GeneratedProposalService = Depends(get_service(GeneratedProposalService)),
):
    try:
        project = await svc.get_project(project_id)
        ensure_tenant_access(project, ctx)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    org_id = ctx.organization_id
    if not body.client_input.strip():
        raise HTTPException(status_code=400, detail="client_input is required")
    await enforce_proposal_limit(org_id)
    doc = await gen_svc.start_generation(
        client_input=body.client_input,
        domain=body.domain,
        project_type=body.project_type,
        org_id=org_id,
        user_id=ctx.user.id,
        idempotency_key=idempotency_key,
        project_id=project_id,
    )
    try:
        generate_proposal_task.delay(
            doc["_id"],
            body.client_input,
            org_id,
            ctx.user.id,
            body.domain,
            body.project_type,
        )
        logger.info("Proposal %s for project %s enqueued to celery", doc["_id"], project_id)
    except Exception as e:
        logger.warning("Celery enqueue failed: %s", e, exc_info=True)
        await gen_svc.delete_proposal(doc["_id"])
        raise HTTPException(
            status_code=503,
            detail="Generation queue unavailable, please retry",
        )
    return doc
