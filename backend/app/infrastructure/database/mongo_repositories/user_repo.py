from typing import Optional
from bson import ObjectId

from app.domain.entities.user import User
from app.domain.interfaces import UserRepository
from app.infrastructure.database.mongodb import get_database


class MongoUserRepository(UserRepository):
    def __init__(self) -> None:
        self.collection_name = "users"

    async def _collection(self):
        db = await get_database()
        return db[self.collection_name]

    async def create(self, user: User) -> User:
        col = await self._collection()
        data = user.model_dump(exclude={"id"}, by_alias=False)
        result = await col.insert_one(data)
        user.id = str(result.inserted_id)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        col = await self._collection()
        data = await col.find_one({"_id": ObjectId(user_id)})
        return User(**data) if data else None

    async def get_by_email(self, email: str) -> Optional[User]:
        col = await self._collection()
        data = await col.find_one({"email": email})
        return User(**data) if data else None

    async def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 100) -> list[User]:
        col = await self._collection()
        cursor = col.find({"organization_id": org_id}).skip(skip).limit(limit)
        return [User(**d) async for d in cursor]

    async def update(self, user: User) -> User:
        col = await self._collection()
        data = user.model_dump(exclude={"id"}, by_alias=False)
        await col.update_one({"_id": ObjectId(user.id)}, {"$set": data})
        return user

    async def delete(self, user_id: str) -> None:
        col = await self._collection()
        await col.delete_one({"_id": ObjectId(user_id)})

    async def count_by_organization(self, org_id: str) -> int:
        col = await self._collection()
        return await col.count_documents({"organization_id": org_id})
