from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.domain.entities.user import User
from app.schemas.project import ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.project_service import ProjectService
from app.api.deps import get_current_user, get_current_org, require_permission

router = APIRouter()


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    body: ProjectCreateRequest,
    user: User = Depends(require_permission("project:create")),
    org_id: str = Depends(get_current_org),
):
    svc = ProjectService()
    project = await svc.create_project(body.model_dump(exclude_unset=True), org_id, user.id)
    return ProjectResponse(**project.model_dump(by_alias=True))


@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    skip: int = 0, limit: int = 100,
    workspace_id: Optional[str] = Query(None),
    user: User = Depends(require_permission("project:read")),
    org_id: str = Depends(get_current_org),
):
    svc = ProjectService()
    projects = await svc.list_projects(org_id, skip=skip, limit=limit, workspace_id=workspace_id)
    items = [ProjectResponse(**p.model_dump(by_alias=True)) for p in projects]
    return PaginatedResponse(items=items, total=len(items), skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    user: User = Depends(require_permission("project:read")),
):
    svc = ProjectService()
    try:
        project = await svc.get_project(project_id)
        if project.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return ProjectResponse(**project.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str, body: ProjectUpdateRequest,
    user: User = Depends(require_permission("project:update")),
):
    svc = ProjectService()
    try:
        project = await svc.update_project(project_id, body.model_dump(exclude_unset=True))
        if project.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return ProjectResponse(**project.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: str,
    user: User = Depends(require_permission("project:delete")),
):
    svc = ProjectService()
    try:
        project = await svc.get_project(project_id)
        if project.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        await svc.delete_project(project_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MessageResponse(message="Project archived")
