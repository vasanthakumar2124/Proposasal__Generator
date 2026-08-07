from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.project_service import ProjectService
from app.infrastructure.di.container import get_service
from app.middleware.tenant_context import TenantContext, get_tenant_context, ensure_tenant_access

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreateRequest,
    ctx: TenantContext = Depends(get_tenant_context("project:create")),
    svc: ProjectService = Depends(get_service(ProjectService)),
):
    project = await svc.create_project(body.model_dump(exclude_unset=True), ctx.organization_id, ctx.user.id)
    return ProjectResponse(**project.model_dump(by_alias=True))


@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    skip: int = 0, limit: int = 100,
    workspace_id: Optional[str] = Query(None),
    ctx: TenantContext = Depends(get_tenant_context("project:read")),
    svc: ProjectService = Depends(get_service(ProjectService)),
):
    projects = await svc.list_projects(ctx.organization_id, skip=skip, limit=limit, workspace_id=workspace_id)
    items = [ProjectResponse(**p.model_dump(by_alias=True)) for p in projects]
    return PaginatedResponse(items=items, total=len(items), skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    ctx: TenantContext = Depends(get_tenant_context("project:read")),
    svc: ProjectService = Depends(get_service(ProjectService)),
):
    try:
        project = await svc.get_project(project_id)
        ensure_tenant_access(project, ctx)
        return ProjectResponse(**project.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str, body: ProjectUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context("project:update")),
    svc: ProjectService = Depends(get_service(ProjectService)),
):
    try:
        project = await svc.update_project(project_id, body.model_dump(exclude_unset=True))
        ensure_tenant_access(project, ctx)
        return ProjectResponse(**project.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: str,
    ctx: TenantContext = Depends(get_tenant_context("project:delete")),
    svc: ProjectService = Depends(get_service(ProjectService)),
):
    try:
        project = await svc.get_project(project_id)
        ensure_tenant_access(project, ctx)
        await svc.delete_project(project_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MessageResponse(message="Project archived")
