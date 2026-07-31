from typing import Optional

from app.domain.entities.workspace import Workspace
from app.domain.exceptions import EntityNotFoundError
from app.domain.interfaces import WorkspaceRepository
from app.infrastructure.database.mongo_repositories.workspace_repo import MongoWorkspaceRepository
from app.infrastructure.log.audit import create_audit_log


class WorkspaceService:
    def __init__(self, workspace_repo: Optional[WorkspaceRepository] = None) -> None:
        self.workspace_repo = workspace_repo or MongoWorkspaceRepository()

    async def create_workspace(self, name: str, description: str, org_id: str, created_by: str) -> Workspace:
        workspace = Workspace(
            name=name,
            description=description,
            organization_id=org_id,
            created_by=created_by,
            members=[created_by],
        )
        workspace = await self.workspace_repo.create(workspace)

        await create_audit_log(
            organization_id=org_id,
            user_id=created_by,
            action="workspace.create",
            resource_type="workspace",
            resource_id=workspace.id,
        )

        return workspace

    async def get_workspace(self, workspace_id: str) -> Workspace:
        workspace = await self.workspace_repo.get_by_id(workspace_id)
        if not workspace or workspace.status != "active":
            raise EntityNotFoundError("Workspace", workspace_id)
        return workspace

    async def update_workspace(
        self, workspace_id: str, name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Workspace:
        workspace = await self.get_workspace(workspace_id)
        if name is not None:
            workspace.name = name
        if description is not None:
            workspace.description = description
        return await self.workspace_repo.update(workspace)

    async def delete_workspace(self, workspace_id: str) -> None:
        await self.get_workspace(workspace_id)
        await self.workspace_repo.delete(workspace_id)

    async def list_workspaces(self, org_id: str, skip: int = 0, limit: int = 100) -> list[Workspace]:
        return await self.workspace_repo.get_by_organization(org_id, skip=skip, limit=limit)

    async def add_member(self, workspace_id: str, user_id: str) -> Workspace:
        workspace = await self.get_workspace(workspace_id)
        if user_id not in workspace.members:
            workspace.members.append(user_id)
        return await self.workspace_repo.add_member(workspace_id, user_id)

    async def remove_member(self, workspace_id: str, user_id: str) -> Workspace:
        workspace = await self.get_workspace(workspace_id)
        if user_id in workspace.members:
            workspace.members.remove(user_id)
        return await self.workspace_repo.remove_member(workspace_id, user_id)
