from typing import Optional
from bson import ObjectId

from app.domain.entities.proposal import Proposal
from app.domain.interfaces import ProposalRepository
from app.infrastructure.database.mongodb import get_database


class MongoProposalRepository(ProposalRepository):
    async def _collection(self):
        db = await get_database()
        return db["proposals"]

    async def create(self, proposal: Proposal) -> Proposal:
        col = await self._collection()
        data = proposal.model_dump(exclude={"id"}, by_alias=False)
        result = await col.insert_one(data)
        proposal.id = str(result.inserted_id)
        return proposal

    async def get_by_id(self, proposal_id: str) -> Optional[Proposal]:
        col = await self._collection()
        data = await col.find_one({"_id": ObjectId(proposal_id)})
        return Proposal(**data) if data else None

    async def get_by_organization(self, org_id: str, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> list[Proposal]:
        col = await self._collection()
        query = {"organization_id": org_id}
        if status:
            query["status"] = status
        cursor = col.find(query).skip(skip).limit(limit).sort("created_at", -1)
        return [Proposal(**d) async for d in cursor]

    async def get_by_project(self, project_id: str) -> list[Proposal]:
        col = await self._collection()
        cursor = col.find({"project_id": project_id}).sort("created_at", -1)
        return [Proposal(**d) async for d in cursor]

    async def update(self, proposal: Proposal) -> Proposal:
        col = await self._collection()
        data = proposal.model_dump(exclude={"id"}, by_alias=False)
        await col.update_one({"_id": ObjectId(proposal.id)}, {"$set": data})
        return proposal

    async def delete(self, proposal_id: str) -> None:
        col = await self._collection()
        await col.update_one({"_id": ObjectId(proposal_id)}, {"$set": {"status": "archived"}})

    async def count_by_organization(self, org_id: str, status: Optional[str] = None) -> int:
        col = await self._collection()
        query = {"organization_id": org_id}
        if status:
            query["status"] = status
        return await col.count_documents(query)
