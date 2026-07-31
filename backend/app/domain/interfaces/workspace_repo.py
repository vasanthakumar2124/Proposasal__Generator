from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.workspace import Workspace


class WorkspaceRepository(ABC):
    @abstractmethod
    async def create(self, workspace: Workspace) -> Workspace:
        pass

    @abstractmethod
    async def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        pass

    @abstractmethod
    async def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 100) -> list[Workspace]:
        pass

    @abstractmethod
    async def update(self, workspace: Workspace) -> Workspace:
        pass

    @abstractmethod
    async def delete(self, workspace_id: str) -> None:
        pass

    @abstractmethod
    async def add_member(self, workspace_id: str, user_id: str) -> Workspace:
        pass

    @abstractmethod
    async def remove_member(self, workspace_id: str, user_id: str) -> Workspace:
        pass

    @abstractmethod
    async def count_by_organization(self, org_id: str) -> int:
        pass
