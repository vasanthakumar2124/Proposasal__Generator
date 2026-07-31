from fastapi import APIRouter, Depends, HTTPException

from app.domain.entities.user import User
from app.schemas.workspace import WorkspaceCreateRequest, WorkspaceUpdateRequest, WorkspaceResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.workspace_service import WorkspaceService
from app.api.deps import get_current_user, get_current_org, require_permission

router = APIRouter()


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    body: WorkspaceCreateRequest,
    user: User = Depends(require_permission("workspace:create")),
    org_id: str = Depends(get_current_org),
):
    svc = WorkspaceService()
    ws = await svc.create_workspace(
        name=body.name,
        description=body.description,
        org_id=org_id,
        created_by=user.id,
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
    user: User = Depends(require_permission("workspace:read")),
    org_id: str = Depends(get_current_org),
):
    svc = WorkspaceService()
    workspaces = await svc.list_workspaces(org_id, skip=skip, limit=limit)
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
    user: User = Depends(require_permission("workspace:read")),
):
    svc = WorkspaceService()
    try:
        ws = await svc.get_workspace(workspace_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    if ws.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

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
    user: User = Depends(require_permission("workspace:update")),
):
    svc = WorkspaceService()
    try:
        ws = await svc.update_workspace(
            workspace_id=workspace_id,
            name=body.name,
            description=body.description,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    if ws.organization_id != user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return WorkspaceResponse(
        _id=ws.id, organization_id=ws.organization_id, name=ws.name,
        description=ws.description, created_by=ws.created_by,
        members=ws.members, status=ws.status,
        created_at=ws.created_at, updated_at=ws.updated_at,
    )


@router.delete("/{workspace_id}", response_model=MessageResponse)
async def delete_workspace(
    workspace_id: str,
    user: User = Depends(require_permission("workspace:delete")),
):
    svc = WorkspaceService()
    try:
        ws = await svc.get_workspace(workspace_id)
        if ws.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        await svc.delete_workspace(workspace_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MessageResponse(message="Workspace deleted")


@router.post("/{workspace_id}/members/{user_id}", response_model=WorkspaceResponse)
async def add_member(
    workspace_id: str,
    user_id: str,
    user: User = Depends(require_permission("workspace:update")),
):
    svc = WorkspaceService()
    try:
        ws = await svc.get_workspace(workspace_id)
        if ws.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
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
    user: User = Depends(require_permission("workspace:update")),
):
    svc = WorkspaceService()
    try:
        ws = await svc.get_workspace(workspace_id)
        if ws.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        ws = await svc.remove_member(workspace_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return WorkspaceResponse(
        _id=ws.id, organization_id=ws.organization_id, name=ws.name,
        description=ws.description, created_by=ws.created_by,
        members=ws.members, status=ws.status,
        created_at=ws.created_at, updated_at=ws.updated_at,
    )
