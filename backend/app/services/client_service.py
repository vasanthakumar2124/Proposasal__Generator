from typing import Optional

from app.domain.entities.client import Client
from app.domain.events import DomainEvent, EVENT_CLIENT_CREATED
from app.domain.exceptions import EntityNotFoundError
from app.domain.interfaces import ClientRepository
from app.infrastructure.database.mongo_repositories.client_repo import MongoClientRepository
from app.infrastructure.log.audit import create_audit_log
from app.infrastructure.events.bus import event_bus


class ClientService:
    def __init__(self, client_repo: Optional[ClientRepository] = None) -> None:
        self.client_repo = client_repo or MongoClientRepository()

    async def create_client(self, data: dict, org_id: str, user_id: str) -> Client:
        client = Client(organization_id=org_id, created_by=user_id, **data)
        client = await self.client_repo.create(client)
        await create_audit_log(org_id, user_id, "client.create", "client", client.id)
        await event_bus.publish(
            DomainEvent(
                event_type=EVENT_CLIENT_CREATED,
                organization_id=org_id,
                user_id=user_id,
                resource_type="client",
                resource_id=client.id,
                payload={"name": client.name},
            )
        )
        return client

    async def get_client(self, client_id: str) -> Client:
        client = await self.client_repo.get_by_id(client_id)
        if not client or client.status != "active":
            raise EntityNotFoundError("Client", client_id)
        return client

    async def update_client(self, client_id: str, data: dict) -> Client:
        client = await self.get_client(client_id)
        for key, value in data.items():
            if value is not None and hasattr(client, key):
                setattr(client, key, value)
        return await self.client_repo.update(client)

    async def delete_client(self, client_id: str) -> None:
        await self.get_client(client_id)
        await self.client_repo.delete(client_id)

    async def list_clients(self, org_id: str, skip: int = 0, limit: int = 100) -> list[Client]:
        return await self.client_repo.get_by_organization(org_id, skip=skip, limit=limit)
