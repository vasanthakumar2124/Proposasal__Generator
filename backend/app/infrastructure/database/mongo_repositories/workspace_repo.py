from typing import Optional
from bson import ObjectId

from app.domain.entities.workspace import Workspace
from app.domain.interfaces import WorkspaceRepository
from app.infrastructure.database.mongodb import get_database


class MongoWorkspaceRepository(WorkspaceRepository):
    def __init__(self) -> None:
        self.collection_name = "workspaces"

    async def _collection(self):
        db = await get_database()
        return db[self.collection_name]

    async def create(self, workspace: Workspace) -> Workspace:
        col = await self._collection()
        data = workspace.model_dump(exclude={"id"}, by_alias=False)
        result = await col.insert_one(data)
        workspace.id = str(result.inserted_id)
        return workspace

    async def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        col = await self._collection()
        data = await col.find_one({"_id": ObjectId(workspace_id)})
        return Workspace(**data) if data else None

    async def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 100) -> list[Workspace]:
        col = await self._collection()
        cursor = col.find({"organization_id": org_id, "status": "active"}).skip(skip).limit(limit).sort("created_at", -1)
        return [Workspace(**d) async for d in cursor]

    async def update(self, workspace: Workspace) -> Workspace:
        col = await self._collection()
        data = workspace.model_dump(exclude={"id"}, by_alias=False)
        await col.update_one({"_id": ObjectId(workspace.id)}, {"$set": data})
        return workspace

    async def delete(self, workspace_id: str) -> None:
        col = await self._collection()
        await col.update_one({"_id": ObjectId(workspace_id)}, {"$set": {"status": "deleted"}})

    async def add_member(self, workspace_id: str, user_id: str) -> Workspace:
        col = await self._collection()
        await col.update_one({"_id": ObjectId(workspace_id)}, {"$addToSet": {"members": user_id}})
        return await self.get_by_id(workspace_id)

    async def remove_member(self, workspace_id: str, user_id: str) -> Workspace:
        col = await self._collection()
        await col.update_one({"_id": ObjectId(workspace_id)}, {"$pull": {"members": user_id}})
        return await self.get_by_id(workspace_id)

    async def count_by_organization(self, org_id: str) -> int:
        col = await self._collection()
        return await col.count_documents({"organization_id": org_id, "status": "active"})
