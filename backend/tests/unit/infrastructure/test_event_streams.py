import asyncio

import pytest

from app.infrastructure.events.streams import ProposalEventTailer

DOC_A = {"_id": "a", "event_type": "proposal.generated", "payload": {"title": "T1"}, "occurred_at": None}
DOC_B = {"_id": "b", "event_type": "proposal.failed", "payload": {"error": "boom"}, "occurred_at": None}
DOC_C = {"_id": "c", "event_type": "proposal.generated", "payload": {"title": "T2"}, "occurred_at": None}


class ScriptedCursor:
    def __init__(self, collection):
        self.collection = collection

    def sort(self, *args, **kwargs):
        return self

    async def to_list(self, length=None):
        if self.collection.polls >= len(self.collection.schedule):
            return []
        docs = self.collection.schedule[self.collection.polls]
        self.collection.polls += 1
        return docs


class FakeCollection:
    def __init__(self, schedule):
        self.schedule = list(schedule)
        self.polls = 0

    def find(self, *args, **kwargs):
        return ScriptedCursor(self)


class FakeDatabase:
    def __init__(self, schedule):
        self.collection = FakeCollection(schedule)

    @property
    def activity_events(self):
        return self.collection


FAKE_DB = FakeDatabase([[DOC_A, DOC_B], [DOC_A, DOC_B, DOC_C], [DOC_A, DOC_B, DOC_C]])


def test_tailer_yields_events_and_dedupes(monkeypatch):
    async def get_db():
        return FAKE_DB

    monkeypatch.setattr("app.infrastructure.events.streams.get_database", get_db)

    async def collect():
        tailer = ProposalEventTailer("p1", "org-1", poll_interval=0.01)
        out = []
        async for event in tailer.events():
            out.append((event["event_type"], event["payload"]))
            if len(out) == 3:
                break
        return out

    result = asyncio.run(collect())
    assert result == [
        ("proposal.generated", {"title": "T1"}),
        ("proposal.failed", {"error": "boom"}),
        ("proposal.generated", {"title": "T2"}),
    ]


def test_tailer_survives_poll_errors(monkeypatch):
    class ExplodingDatabase:
        @property
        def activity_events(self):
            raise RuntimeError("mongo down")

    async def get_db():
        return ExplodingDatabase()

    monkeypatch.setattr("app.infrastructure.events.streams.get_database", get_db)

    async def collect():
        tailer = ProposalEventTailer("p1", "org-1", poll_interval=0.01)
        aiter = tailer.events()
        await aiter.__anext__()

    with pytest.raises(TimeoutError):
        asyncio.run(asyncio.wait_for(collect(), timeout=0.5))
