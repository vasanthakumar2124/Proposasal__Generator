from typing import Optional

from app.domain.entities.project import Project
from app.domain.exceptions import EntityNotFoundError
from app.domain.interfaces import ProjectRepository
from app.infrastructure.database.mongo_repositories.project_repo import MongoProjectRepository
from app.infrastructure.log.audit import create_audit_log


class ProjectService:
    def __init__(self, project_repo: Optional[ProjectRepository] = None) -> None:
        self.project_repo = project_repo or MongoProjectRepository()

    async def create_project(self, data: dict, org_id: str, user_id: str) -> Project:
        project = Project(organization_id=org_id, created_by=user_id, **data)
        project = await self.project_repo.create(project)
        await create_audit_log(org_id, user_id, "project.create", "project", project.id)
        return project

    async def get_project(self, project_id: str) -> Project:
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)
        return project

    async def update_project(self, project_id: str, data: dict) -> Project:
        project = await self.get_project(project_id)
        for key, value in data.items():
            if value is not None and hasattr(project, key):
                setattr(project, key, value)
        return await self.project_repo.update(project)

    async def delete_project(self, project_id: str) -> None:
        await self.get_project(project_id)
        await self.project_repo.delete(project_id)

    async def list_projects(self, org_id: str, skip: int = 0, limit: int = 100, workspace_id: Optional[str] = None) -> list[Project]:
        return await self.project_repo.get_by_organization(org_id, skip=skip, limit=limit, workspace_id=workspace_id)
