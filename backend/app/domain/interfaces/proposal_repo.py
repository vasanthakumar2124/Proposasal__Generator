from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.proposal import Proposal


class ProposalRepository(ABC):
    @abstractmethod
    async def create(self, proposal: Proposal) -> Proposal:
        pass

    @abstractmethod
    async def get_by_id(self, proposal_id: str) -> Optional[Proposal]:
        pass

    @abstractmethod
    async def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> list[Proposal]:
        pass

    @abstractmethod
    async def get_by_project(self, project_id: str) -> list[Proposal]:
        pass

    @abstractmethod
    async def update(self, proposal: Proposal) -> Proposal:
        pass

    @abstractmethod
    async def delete(self, proposal_id: str) -> None:
        pass

    @abstractmethod
    async def count_by_organization(self, org_id: str, status: Optional[str] = None) -> int:
        pass
