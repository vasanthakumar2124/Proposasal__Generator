from typing import Optional
from bson import ObjectId

from app.domain.entities.organization import Organization
from app.domain.interfaces import OrganizationRepository
from app.infrastructure.database.mongodb import get_database


class MongoOrganizationRepository(OrganizationRepository):
    def __init__(self) -> None:
        self.collection_name = "organizations"

    async def _collection(self):
        db = await get_database()
        return db[self.collection_name]

    async def create(self, org: Organization) -> Organization:
        col = await self._collection()
        data = org.model_dump(exclude={"id"}, by_alias=False)
        result = await col.insert_one(data)
        org.id = str(result.inserted_id)
        return org

    async def get_by_id(self, org_id: str) -> Optional[Organization]:
        col = await self._collection()
        data = await col.find_one({"_id": ObjectId(org_id)})
        return Organization(**data) if data else None

    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        col = await self._collection()
        data = await col.find_one({"slug": slug})
        return Organization(**data) if data else None

    async def update(self, org: Organization) -> Organization:
        col = await self._collection()
        data = org.model_dump(exclude={"id"}, by_alias=False)
        await col.update_one({"_id": ObjectId(org.id)}, {"$set": data})
        return org

    async def delete(self, org_id: str) -> None:
        col = await self._collection()
        await col.delete_one({"_id": ObjectId(org_id)})

    async def list_all(self, skip: int = 0, limit: int = 100) -> list[Organization]:
        col = await self._collection()
        cursor = col.find().skip(skip).limit(limit)
        return [Organization(**d) async for d in cursor]

    async def count(self) -> int:
        col = await self._collection()
        return await col.count_documents({})
