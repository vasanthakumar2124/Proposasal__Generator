import asyncio

import pytest

from app.domain.events import DomainEvent


@pytest.fixture
def event():
    return DomainEvent(
        event_type="proposal.generated",
        organization_id="org-1",
        user_id="user-1",
        resource_type="proposal",
        resource_id="prop-1",
        payload={"title": "Test"},
    )


def test_publish_persists_event(monkeypatch, event):
    from app.infrastructure.events.bus import EventBus

    inserted = {}

    class FakeDb:
        async def insert_one(self, doc):
            inserted.update(doc)

    class FakeDatabase:
        activity_events = FakeDb()

    async def fake_get_database():
        return FakeDatabase()

    monkeypatch.setattr("app.infrastructure.events.bus.get_database", fake_get_database)
    bus = EventBus()
    bus._enabled = True
    asyncio.run(bus.publish(event))
    assert inserted["event_type"] == "proposal.generated"
    assert inserted["organization_id"] == "org-1"
    assert inserted["payload"] == {"title": "Test"}


def test_publish_dispatches_to_handlers(monkeypatch, event):
    from app.infrastructure.events.bus import EventBus

    class FakeDb:
        async def insert_one(self, doc):
            pass

    class FakeDatabase:
        activity_events = FakeDb()

    async def fake_get_database():
        return FakeDatabase()

    monkeypatch.setattr("app.infrastructure.events.bus.get_database", fake_get_database)
    seen = []

    async def handler(ev):
        seen.append(ev.event_type)

    bus = EventBus()
    bus._enabled = True
    bus.subscribe(handler)
    asyncio.run(bus.publish(event))
    assert seen == ["proposal.generated"]


def test_publish_disabled_skips_persist(monkeypatch, event):
    from app.infrastructure.events.bus import EventBus

    called = []

    async def fake_get_database():
        called.append("db")
        return None

    monkeypatch.setattr("app.infrastructure.events.bus.get_database", fake_get_database)
    bus = EventBus()
    bus._enabled = False
    asyncio.run(bus.publish(event))
    assert called == []
