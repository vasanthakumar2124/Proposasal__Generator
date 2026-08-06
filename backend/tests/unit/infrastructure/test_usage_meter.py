import asyncio

from app.infrastructure.usage.context import get_usage_context, set_usage_context
from app.infrastructure.usage.meter import UsageMeter, current_period, METERED_FIELDS


def test_usage_context_defaults_to_empty():
    assert get_usage_context() == ("", "")


def test_usage_context_set_and_get():
    set_usage_context("org-9", "user-9")
    assert get_usage_context() == ("org-9", "user-9")
    set_usage_context("", "")


def test_current_period_format():
    assert len(current_period()) == 7
    assert current_period()[4] == "-"


def test_usage_meter_increments(monkeypatch):
    updates = []

    class FakeDb:
        async def update_one(self, query, update, upsert=False):
            updates.append((query, update))

        async def find_one(self, query):
            return {
                "organization_id": "org-1",
                "period": current_period(),
                "proposals_generated": 2,
                "llm_calls": 5,
                "input_tokens": 100,
                "output_tokens": 50,
                "cost": 0.001,
            }

    class FakeDatabase:
        usage = FakeDb()

    async def fake_get_database():
        return FakeDatabase()

    monkeypatch.setattr("app.infrastructure.usage.meter.get_database", fake_get_database)
    meter = UsageMeter()

    async def run():
        await meter.record_proposal_generation("org-1", "user-1", "prop-1")
        await meter.record_llm_call("org-1", "user-1", "groq", "llama-3.3-70b", 10, 20, 0.0001)
        usage = await meter.get_org_usage("org-1")
        return usage

    usage = asyncio.run(run())
    assert len(updates) == 2
    assert updates[0][0] == {"organization_id": "org-1", "period": current_period()}
    assert updates[0][1]["$inc"] == {"proposals_generated": 1}
    assert updates[1][1]["$inc"] == {"llm_calls": 1, "input_tokens": 10, "output_tokens": 20, "cost": 0.0001}
    assert usage["proposals_generated"] == 2
    assert set(k in usage for k in METERED_FIELDS)


def test_usage_meter_disabled_skips(monkeypatch):
    from app.config.settings import settings

    monkeypatch.setattr(settings, "ENABLE_USAGE_METERING", False)
    called = []

    async def fake_get_database():
        called.append("db")
        return None

    monkeypatch.setattr("app.infrastructure.usage.meter.get_database", fake_get_database)
    meter = UsageMeter()
    asyncio.run(meter.record_proposal_generation("org-1", "user-1", "prop-1"))
    assert called == []
