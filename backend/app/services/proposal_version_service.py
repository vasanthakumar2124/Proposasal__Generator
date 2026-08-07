import logging
from datetime import datetime, timezone

from bson import ObjectId

from app.domain.events import DomainEvent, EVENT_PROPOSAL_VERSION_CREATED
from app.domain.exceptions import EntityNotFoundError
from app.infrastructure.database.mongodb import get_database
from app.infrastructure.events.bus import event_bus

logger = logging.getLogger("proposalcraft.proposal_version_service")

VERSION_COLLECTION = "proposal_versions"
# Proposal docs live in one of two collections: AI-generated (dict docs)
# or manually created (Proposal entities). Versioning is agnostic to which.
_PROPOSAL_COLLECTIONS = ("generated_proposals", "proposals")


class ProposalVersionService:
    async def _versions(self):
        db = await get_database()
        return db[VERSION_COLLECTION]

    async def _locate(self, proposal_id: str, org_id: str) -> tuple[str, dict]:
        """Return (collection_name, doc) for a tenant-owned proposal."""
        db = await get_database()
        oid = ObjectId(proposal_id)
        for name in _PROPOSAL_COLLECTIONS:
            doc = await db[name].find_one({"_id": oid, "organization_id": org_id})
            if doc:
                return name, doc
        raise EntityNotFoundError("Proposal", proposal_id)

    async def create_version(
        self,
        proposal_id: str,
        org_id: str,
        user_id: str,
        title: str | None = None,
        sections: dict | None = None,
        note: str | None = None,
        parent_version: int | None = None,
    ) -> dict:
        """Snapshot the current content of a proposal as an immutable version."""
        _, doc = await self._locate(proposal_id, org_id)
        versions = await self._versions()
        latest = await versions.find_one({"proposal_id": proposal_id}, sort=[("version", -1)])
        next_version = (latest or {}).get("version", 0) + 1

        snapshot = {
            "_id": ObjectId(),
            "proposal_id": proposal_id,
            "version": next_version,
            "author_id": user_id,
            "title": title or doc.get("title", "Untitled"),
            "sections_snapshot": sections if sections is not None else doc.get("sections", {}),
            "status": doc.get("status", "draft"),
            "note": note,
            "parent_version": parent_version,
            "created_at": datetime.now(timezone.utc),
        }
        await versions.insert_one(snapshot)
        snapshot["_id"] = str(snapshot["_id"])
        logger.info("Proposal %s version %d snapshotted", proposal_id, next_version)
        await event_bus.publish(
            DomainEvent(
                event_type=EVENT_PROPOSAL_VERSION_CREATED,
                organization_id=org_id,
                user_id=user_id,
                resource_type="proposal",
                resource_id=proposal_id,
                payload={"version": next_version, "note": note},
            )
        )
        return snapshot

    async def list_versions(self, proposal_id: str, org_id: str) -> list[dict]:
        await self._locate(proposal_id, org_id)
        versions = await self._versions()
        cursor = versions.find({"proposal_id": proposal_id}).sort("version", -1)
        items = []
        async for v in cursor:
            v["_id"] = str(v["_id"])
            items.append(v)
        return items

    async def get_version(self, proposal_id: str, version_id: str, org_id: str) -> dict:
        await self._locate(proposal_id, org_id)
        versions = await self._versions()
        v = await versions.find_one({"_id": ObjectId(version_id), "proposal_id": proposal_id})
        if not v:
            raise EntityNotFoundError("Proposal version", version_id)
        v["_id"] = str(v["_id"])
        return v

    async def restore_version(self, proposal_id: str, version_id: str, org_id: str, user_id: str) -> dict:
        """Restore a snapshot onto the live proposal; the restore itself
        becomes a new version so history is never lost."""
        snapshot = await self.get_version(proposal_id, version_id, org_id)
        collection_name, _ = await self._locate(proposal_id, org_id)

        db = await get_database()
        versions = await self._versions()
        latest = await versions.find_one({"proposal_id": proposal_id}, sort=[("version", -1)])
        new_version = (latest or {}).get("version", 0) + 1
        now = datetime.now(timezone.utc)

        await db[collection_name].update_one(
            {"_id": ObjectId(proposal_id)},
            {
                "$set": {
                    "sections": snapshot["sections_snapshot"],
                    "version": new_version,
                    "updated_at": now,
                }
            },
        )

        restored = await self.create_version(
            proposal_id,
            org_id,
            user_id,
            title=snapshot["title"],
            sections=snapshot["sections_snapshot"],
            note=f"restored from version {snapshot['version']}",
            parent_version=snapshot["version"],
        )
        return restored

    async def diff_versions(
        self, proposal_id: str, from_version_id: str, to_version_id: str, org_id: str
    ) -> dict:
        from_v = await self.get_version(proposal_id, from_version_id, org_id)
        to_v = await self.get_version(proposal_id, to_version_id, org_id)
        from_sections = from_v.get("sections_snapshot", {})
        to_sections = to_v.get("sections_snapshot", {})
        changes: dict = {}
        for section in set(from_sections) | set(to_sections):
            old = from_sections.get(section)
            new = to_sections.get(section)
            if old != new:
                changes[section] = {"from": old, "to": new}
        return {
            "proposal_id": proposal_id,
            "from_version": from_v["version"],
            "to_version": to_v["version"],
            "changes": changes,
        }
