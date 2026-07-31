from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.client import Client


class ClientRepository(ABC):
    @abstractmethod
    async def create(self, client: Client) -> Client:
        pass

    @abstractmethod
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        pass

    @abstractmethod
    async def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 100) -> list[Client]:
        pass

    @abstractmethod
    async def update(self, client: Client) -> Client:
        pass

    @abstractmethod
    async def delete(self, client_id: str) -> None:
        pass

    @abstractmethod
    async def count_by_organization(self, org_id: str) -> int:
        pass
