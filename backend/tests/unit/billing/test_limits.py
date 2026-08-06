import pytest
from fastapi import HTTPException

from app.billing.limits import enforce_proposal_limit, get_org_plan_state


class FakeSubscription:
    plan_id = "free"


async def fake_no_subscription(org_id):
    return None


async def fake_subscription(org_id):
    return FakeSubscription()


async def fake_usage_2(org_id):
    return {"proposals_generated": 2, "period": "2026-08"}


async def fake_usage_3(org_id):
    return {"proposals_generated": 3, "period": "2026-08"}


def test_state_free_plan_remaining(monkeypatch):
    monkeypatch.setattr("app.billing.limits.stripe_service.get_subscription", fake_subscription)
    monkeypatch.setattr("app.billing.limits.usage_meter.get_org_usage", fake_usage_2)
    state = asyncio_run(get_org_plan_state("org-1"))
    assert state["plan_id"] == "free"
    assert state["proposals_used"] == 2
    assert state["proposals_remaining"] == 1


def test_enforce_passes_under_limit(monkeypatch):
    monkeypatch.setattr("app.billing.limits.stripe_service.get_subscription", fake_subscription)
    monkeypatch.setattr("app.billing.limits.usage_meter.get_org_usage", fake_usage_2)
    asyncio_run(enforce_proposal_limit("org-1"))


def test_enforce_blocks_at_limit(monkeypatch):
    monkeypatch.setattr("app.billing.limits.stripe_service.get_subscription", fake_subscription)
    monkeypatch.setattr("app.billing.limits.usage_meter.get_org_usage", fake_usage_3)
    with pytest.raises(HTTPException) as exc_info:
        asyncio_run(enforce_proposal_limit("org-1"))
    assert exc_info.value.status_code == 402
    assert "limit reached" in exc_info.value.detail


def test_enforce_skipped_when_metering_disabled(monkeypatch):
    from app.config.settings import settings

    monkeypatch.setattr(settings, "ENABLE_USAGE_METERING", False)
    monkeypatch.setattr("app.billing.limits.stripe_service.get_subscription", fake_subscription)
    monkeypatch.setattr("app.billing.limits.usage_meter.get_org_usage", fake_usage_3)
    asyncio_run(enforce_proposal_limit("org-1"))


def test_free_default_when_no_subscription(monkeypatch):
    monkeypatch.setattr("app.billing.limits.stripe_service.get_subscription", fake_no_subscription)
    monkeypatch.setattr("app.billing.limits.usage_meter.get_org_usage", fake_usage_2)
    state = asyncio_run(get_org_plan_state("org-1"))
    assert state["plan_id"] == "free"


def asyncio_run(coro):
    import asyncio

    return asyncio.run(coro)
