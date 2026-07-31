from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.project import Project


class ProjectRepository(ABC):
    @abstractmethod
    async def create(self, project: Project) -> Project:
        pass

    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional[Project]:
        pass

    @abstractmethod
    async def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 100, workspace_id: Optional[str] = None) -> list[Project]:
        pass

    @abstractmethod
    async def update(self, project: Project) -> Project:
        pass

    @abstractmethod
    async def delete(self, project_id: str) -> None:
        pass

    @abstractmethod
    async def count_by_organization(self, org_id: str) -> int:
        pass
