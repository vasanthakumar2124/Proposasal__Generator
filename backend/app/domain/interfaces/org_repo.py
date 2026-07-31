from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.organization import Organization


class OrganizationRepository(ABC):
    @abstractmethod
    async def create(self, org: Organization) -> Organization:
        pass

    @abstractmethod
    async def get_by_id(self, org_id: str) -> Optional[Organization]:
        pass

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        pass

    @abstractmethod
    async def update(self, org: Organization) -> Organization:
        pass

    @abstractmethod
    async def delete(self, org_id: str) -> None:
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Organization]:
        pass

    @abstractmethod
    async def count(self) -> int:
        pass
