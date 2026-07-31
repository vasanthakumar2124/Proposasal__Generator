from typing import Optional
from bson import ObjectId

from app.domain.entities.client import Client
from app.domain.interfaces import ClientRepository
from app.infrastructure.database.mongodb import get_database


class MongoClientRepository(ClientRepository):
    async def _collection(self):
        db = await get_database()
        return db["clients"]

    async def create(self, client: Client) -> Client:
        col = await self._collection()
        data = client.model_dump(exclude={"id"}, by_alias=False)
        result = await col.insert_one(data)
        client.id = str(result.inserted_id)
        return client

    async def get_by_id(self, client_id: str) -> Optional[Client]:
        col = await self._collection()
        data = await col.find_one({"_id": ObjectId(client_id)})
        return Client(**data) if data else None

    async def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 100) -> list[Client]:
        col = await self._collection()
        cursor = col.find({"organization_id": org_id, "status": "active"}).skip(skip).limit(limit).sort("name", 1)
        return [Client(**d) async for d in cursor]

    async def update(self, client: Client) -> Client:
        col = await self._collection()
        data = client.model_dump(exclude={"id"}, by_alias=False)
        await col.update_one({"_id": ObjectId(client.id)}, {"$set": data})
        return client

    async def delete(self, client_id: str) -> None:
        col = await self._collection()
        await col.update_one({"_id": ObjectId(client_id)}, {"$set": {"status": "deleted"}})

    async def count_by_organization(self, org_id: str) -> int:
        col = await self._collection()
        return await col.count_documents({"organization_id": org_id, "status": "active"})
