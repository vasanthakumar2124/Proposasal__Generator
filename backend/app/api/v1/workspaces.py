from fastapi import APIRouter, Depends, HTTPException

from app.schemas.workspace import WorkspaceCreateRequest, WorkspaceUpdateRequest, WorkspaceResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.workspace_service import WorkspaceService
from app.infrastructure.di.container import get_service
from app.middleware.tenant_context import TenantContext, get_tenant_context, ensure_tenant_access

router = APIRouter()


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    body: WorkspaceCreateRequest,
    ctx: TenantContext = Depends(get_tenant_context("workspace:create")),
    svc: WorkspaceService = Depends(get_service(WorkspaceService)),
):
    ws = await svc.create_workspace(
        name=body.name,
        description=body.description,
        org_id=ctx.organization_id,
        created_by=ctx.user.id,
    )
    return WorkspaceResponse(
        _id=ws.id, organization_id=ws.organization_id, name=ws.name,
        description=ws.description, created_by=ws.created_by,
        members=ws.members, status=ws.status,
        created_at=ws.created_at, updated_at=ws.updated_at,
    )


@router.get("", response_model=PaginatedResponse[WorkspaceResponse])
async def list_workspaces(
    skip: int = 0,
    limit: int = 100,
    ctx: TenantContext = Depends(get_tenant_context("workspace:read")),
    svc: WorkspaceService = Depends(get_service(WorkspaceService)),
):
    workspaces = await svc.list_workspaces(ctx.organization_id, skip=skip, limit=limit)
    items = [WorkspaceResponse(
        _id=w.id, organization_id=w.organization_id, name=w.name,
        description=w.description, created_by=w.created_by,
        members=w.members, status=w.status,
        created_at=w.created_at, updated_at=w.updated_at,
    ) for w in workspaces]
    return PaginatedResponse(items=items, total=len(items), skip=skip, limit=limit)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    ctx: TenantContext = Depends(get_tenant_context("workspace:read")),
    svc: WorkspaceService = Depends(get_service(WorkspaceService)),
):
    try:
        ws = await svc.get_workspace(workspace_id)
        ensure_tenant_access(ws, ctx)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    return WorkspaceResponse(
        _id=ws.id, organization_id=ws.organization_id, name=ws.name,
        description=ws.description, created_by=ws.created_by,
        members=ws.members, status=ws.status,
        created_at=ws.created_at, updated_at=ws.updated_at,
    )


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: str,
    body: WorkspaceUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context("workspace:update")),
    svc: WorkspaceService = Depends(get_service(WorkspaceService)),
):
    try:
        existing = await svc.get_workspace(workspace_id)
        ensure_tenant_access(existing, ctx)
        ws = await svc.update_workspace(
            workspace_id=workspace_id,
            name=body.name,
            description=body.description,
        )
        ensure_tenant_access(ws, ctx)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    return WorkspaceResponse(
        _id=ws.id, organization_id=ws.organization_id, name=ws.name,
        description=ws.description, created_by=ws.created_by,
        members=ws.members, status=ws.status,
        created_at=ws.created_at, updated_at=ws.updated_at,
    )


@router.delete("/{workspace_id}", response_model=MessageResponse)
async def delete_workspace(
    workspace_id: str,
    ctx: TenantContext = Depends(get_tenant_context("workspace:delete")),
    svc: WorkspaceService = Depends(get_service(WorkspaceService)),
):
    try:
        ws = await svc.get_workspace(workspace_id)
        ensure_tenant_access(ws, ctx)
        await svc.delete_workspace(workspace_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MessageResponse(message="Workspace deleted")


@router.post("/{workspace_id}/members/{user_id}", response_model=WorkspaceResponse)
async def add_member(
    workspace_id: str,
    user_id: str,
    ctx: TenantContext = Depends(get_tenant_context("workspace:update")),
    svc: WorkspaceService = Depends(get_service(WorkspaceService)),
):
    try:
        ws = await svc.get_workspace(workspace_id)
        ensure_tenant_access(ws, ctx)
        ws = await svc.add_member(workspace_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return WorkspaceResponse(
        _id=ws.id, organization_id=ws.organization_id, name=ws.name,
        description=ws.description, created_by=ws.created_by,
        members=ws.members, status=ws.status,
        created_at=ws.created_at, updated_at=ws.updated_at,
    )


@router.delete("/{workspace_id}/members/{user_id}", response_model=WorkspaceResponse)
async def remove_member(
    workspace_id: str,
    user_id: str,
    ctx: TenantContext = Depends(get_tenant_context("workspace:update")),
    svc: WorkspaceService = Depends(get_service(WorkspaceService)),
):
    try:
        ws = await svc.get_workspace(workspace_id)
        ensure_tenant_access(ws, ctx)
        ws = await svc.remove_member(workspace_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return WorkspaceResponse(
        _id=ws.id, organization_id=ws.organization_id, name=ws.name,
        description=ws.description, created_by=ws.created_by,
        members=ws.members, status=ws.status,
        created_at=ws.created_at, updated_at=ws.updated_at,
    )
