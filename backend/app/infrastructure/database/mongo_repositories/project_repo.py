from typing import Optional
from bson import ObjectId

from app.domain.entities.project import Project
from app.domain.interfaces import ProjectRepository
from app.infrastructure.database.mongodb import get_database


class MongoProjectRepository(ProjectRepository):
    async def _collection(self):
        db = await get_database()
        return db["projects"]

    async def create(self, project: Project) -> Project:
        col = await self._collection()
        data = project.model_dump(exclude={"id"}, by_alias=False)
        result = await col.insert_one(data)
        project.id = str(result.inserted_id)
        return project

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        col = await self._collection()
        data = await col.find_one({"_id": ObjectId(project_id)})
        return Project(**data) if data else None

    async def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 100, workspace_id: Optional[str] = None) -> list[Project]:
        col = await self._collection()
        query = {"organization_id": org_id}
        if workspace_id:
            query["workspace_id"] = workspace_id
        cursor = col.find(query).skip(skip).limit(limit).sort("created_at", -1)
        return [Project(**d) async for d in cursor]

    async def update(self, project: Project) -> Project:
        col = await self._collection()
        data = project.model_dump(exclude={"id"}, by_alias=False)
        await col.update_one({"_id": ObjectId(project.id)}, {"$set": data})
        return project

    async def delete(self, project_id: str) -> None:
        col = await self._collection()
        await col.update_one({"_id": ObjectId(project_id)}, {"$set": {"status": "archived"}})

    async def count_by_organization(self, org_id: str) -> int:
        col = await self._collection()
        return await col.count_documents({"organization_id": org_id})
