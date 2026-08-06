import asyncio
from typing import AsyncIterator

from app.domain.events import EVENT_PROPOSAL_FAILED, EVENT_PROPOSAL_GENERATED
from app.infrastructure.database.mongodb import get_database
from app.infrastructure.log.logger import logger

STATUS_EVENT_TYPES = (EVENT_PROPOSAL_GENERATED, EVENT_PROPOSAL_FAILED)


class ProposalEventTailer:
    """Tails activity_events for a proposal, yielding status events newest-last.

    Uses an indexed poll over the durable event store (works on standalone
    MongoDB where change streams are unavailable).
    """

    def __init__(self, proposal_id: str, org_id: str, poll_interval: float = 2.0) -> None:
        self.proposal_id = proposal_id
        self.org_id = org_id
        self.poll_interval = poll_interval
        self._seen: set[str] = set()

    async def events(self) -> AsyncIterator[dict]:
        while True:
            try:
                docs = await self._fetch_events()
                for doc in docs:
                    event_id = str(doc["_id"])
                    if event_id in self._seen:
                        continue
                    self._seen.add(event_id)
                    yield {
                        "event_type": doc["event_type"],
                        "payload": doc.get("payload", {}),
                        "occurred_at": doc.get("occurred_at"),
                    }
            except Exception as e:
                logger.error("Event tailer poll failed for %s: %s", self.proposal_id, e)
            await asyncio.sleep(self.poll_interval)

    async def _fetch_events(self) -> list[dict]:
        db = await get_database()
        cursor = db.activity_events.find(
            {
                "organization_id": self.org_id,
                "resource_id": self.proposal_id,
                "event_type": {"$in": list(STATUS_EVENT_TYPES)},
            }
        ).sort("occurred_at", 1)
        return await cursor.to_list(length=None)
