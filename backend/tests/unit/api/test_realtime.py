import asyncio
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domain.entities.user import User
from app.api.v1.realtime import router, get_sse_user


class FakeTailer:
    def __init__(self, proposal_id, org_id, poll_interval=2.0):
        pass

    async def events(self):
        yield {
            "event_type": "proposal.generated",
            "payload": {"title": "Inventory Tracking System", "error": None},
            "occurred_at": None,
        }


class FakeProposalService:
    async def get_proposal(self, proposal_id):
        return {
            "_id": proposal_id,
            "status": "processing",
            "title": "Generating proposal...",
            "error": None,
            "organization_id": "org-123",
        }


class FakeUser(User):
    def __init__(self):
        super().__init__(
            id="user-1",
            organization_id="org-123",
            email="test@test.com",
            name="Test User",
            role="admin",
            password_hash="",
            permissions=[],
            status="active",
        )

    def has_permission(self, permission):
        return True


def make_client(monkeypatch):
    monkeypatch.setattr("app.api.v1.realtime.ProposalEventTailer", FakeTailer)
    monkeypatch.setattr("app.api.v1.realtime.GeneratedProposalService", FakeProposalService)

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_sse_user] = lambda: FakeUser()
    return TestClient(app)


def test_stream_sends_connected_then_status(monkeypatch):
    client = make_client(monkeypatch)
    with client.stream("GET", "/proposals/abc123/events") as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        assert r.headers["cache-control"] == "no-cache"
        events = []
        data_payloads = []
        for line in r.iter_lines():
            if line.startswith("event:"):
                events.append(line.split(":", 1)[1].strip())
            elif line.startswith("data:"):
                data_payloads.append(json.loads(line.split(":", 1)[1].strip()))
                if data_payloads[-1].get("event_type") == "proposal.generated":
                    break
        assert events == ["connected", "status"]
        assert data_payloads[0]["status"] == "processing"
        assert data_payloads[1]["status"] == "draft"
        assert data_payloads[1]["title"] == "Inventory Tracking System"


def test_stream_requires_owner_org(monkeypatch):
    client = make_client(monkeypatch)

    def wrong_org_user():
        u = FakeUser()
        u.organization_id = "org-999"
        return u

    client.app.dependency_overrides[get_sse_user] = wrong_org_user
    with client.stream("GET", "/proposals/abc123/events") as r:
        assert r.status_code == 404


def test_stream_missing_proposal_404(monkeypatch):
    client = make_client(monkeypatch)

    class MissingProposalService:
        async def get_proposal(self, proposal_id):
            return None

    monkeypatch.setattr("app.api.v1.realtime.GeneratedProposalService", MissingProposalService)
    with client.stream("GET", "/proposals/def456/events") as r:
        assert r.status_code == 404
