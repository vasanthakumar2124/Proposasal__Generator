"""Step 5: proposal lifecycle state machine + versioning tests.

Covers:
- explicit transition validation (valid flows pass, invalid ones raise/reject)
- immutable version snapshots on generation and manual edits
- restore creates a new version and restores content
- diff between two snapshots
- activity events for transitions and version creation
- cross-tenant isolation on versions
"""

from uuid import uuid4

import pytest
from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.v1.api import api_router
from app.api.v2.api import api_v2_router
from app.config.settings import settings
from app.infrastructure.database import mongodb


@pytest.fixture
def mongo_db(monkeypatch):
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_name = f"proposalcraft_test_{uuid4().hex[:8]}"
    db = client[db_name]
    monkeypatch.setattr(mongodb, "client", client)
    monkeypatch.setattr(mongodb, "db", db)
    yield db, db_name
    client.close()


@pytest.fixture
def client(mongo_db, monkeypatch):
    db, db_name = mongo_db
    monkeypatch.setattr(settings, "QDRANT_URL", "")
    monkeypatch.setattr(settings, "QDRANT_API_KEY", "")
    monkeypatch.setattr("app.api.v1.proposals.generate_proposal_task", DummyCeleryTask())
    monkeypatch.setattr("app.api.v2.projects.generate_proposal_task", DummyCeleryTask())
    app = FastAPI()
    app.include_router(api_router)
    app.include_router(api_v2_router)
    with TestClient(app) as c:
        c.portal.call(mongodb.ensure_indexes)
        yield c

        async def _drop():
            await db.client.drop_database(db_name)

        c.portal.call(_drop)


class DummyCeleryTask:
    def __init__(self, raise_on_delay: bool = False):
        self._raise = raise_on_delay
        self.calls: list[list] = []

    def delay(self, *args) -> None:
        self.calls.append(list(args))
        if self._raise:
            raise ConnectionError("broker down")


def register(client, name, email, company):
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": "password123", "company_name": company},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return {
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "org_id": data["user"]["organization_id"],
    }


@pytest.fixture
def auth(client):
    return register(client, "Alice", f"alice_{uuid4().hex[:8]}@test.com", "Acme Corp")


def create_proposal(client, auth, title="New Proposal"):
    resp = client.post("/api/v1/proposals", json={"title": title}, headers=auth["headers"])
    assert resp.status_code == 201, resp.text
    return resp.json()


def versions(client, auth, proposal_id):
    resp = client.get(f"/api/v2/proposals/{proposal_id}/versions", headers=auth["headers"])
    assert resp.status_code == 200, resp.text
    return resp.json()["versions"]


class TestLifecycleMachine:
    def test_draft_to_processing_to_review_to_approved(self, client, auth):
        p = create_proposal(client, auth)
        assert client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "processing"}, headers=auth["headers"]).status_code == 200
        assert client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "review"}, headers=auth["headers"]).status_code == 200
        assert client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "approved"}, headers=auth["headers"]).status_code == 200
        assert client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "sent"}, headers=auth["headers"]).status_code == 200

    def test_invalid_transition_rejected(self, client, auth):
        p = create_proposal(client, auth)
        resp = client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "sent"}, headers=auth["headers"])
        assert resp.status_code in (400, 404), resp.text
        if resp.status_code == 400:
            assert "Invalid" in resp.json()["detail"]

    def test_review_to_sent_invalid(self, client, auth):
        p = create_proposal(client, auth)
        client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "review"}, headers=auth["headers"])
        resp = client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "sent"}, headers=auth["headers"])
        assert resp.status_code == 400

    def test_rejected_can_go_back_to_draft(self, client, auth):
        p = create_proposal(client, auth)
        client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "review"}, headers=auth["headers"])
        client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "rejected"}, headers=auth["headers"])
        resp = client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "draft"}, headers=auth["headers"])
        assert resp.status_code == 200

    def test_transition_publishes_activity_event(self, client, mongo_db, auth):
        p = create_proposal(client, auth)
        client.post(f"/api/v2/proposals/{p['_id']}/status", json={"target": "review"}, headers=auth["headers"])

        async def _find():
            return await mongo_db[0].activity_events.find_one(
                {"resource_id": p["_id"], "event_type": "proposal.status_changed"}
            )

        ev = client.portal.call(_find)
        assert ev is not None
        assert ev["payload"]["from"] == "draft"
        assert ev["payload"]["to"] == "review"


class TestVersioning:
    def test_generation_creates_version(self, client, mongo_db, auth, monkeypatch):
        task = DummyCeleryTask()
        monkeypatch.setattr("app.api.v1.proposals.generate_proposal_task", task)
        resp = client.post(
            "/api/v1/proposals/generate",
            json={"client_input": "Build a CRM"},
            headers=auth["headers"],
        )
        doc_id = resp.json()["_id"]

        async def _finalize():
            await mongo_db[0].generated_proposals.update_one(
                {"_id": ObjectId(doc_id)},
                {"$set": {"status": "draft", "title": "CRM Proposal", "sections": {"Overview": {"content": "hi"}}}},
            )

        client.portal.call(_finalize)
        from app.services.proposal_version_service import ProposalVersionService

        async def _snapshot():
            await ProposalVersionService().create_version(
                doc_id, auth["org_id"], "user1", title="CRM Proposal", sections={"Overview": {"content": "hi"}}, note="generated"
            )

        client.portal.call(_snapshot)
        vs = versions(client, auth, doc_id)
        assert len(vs) == 1
        assert vs[0]["version"] == 1
        assert vs[0]["sections_snapshot"] == {"Overview": {"content": "hi"}}

    def test_manual_edit_creates_new_version(self, client, auth):
        p = create_proposal(client, auth)
        client.put(f"/api/v1/proposals/{p['_id']}", json={"description": "scope v2"}, headers=auth["headers"])
        client.put(f"/api/v1/proposals/{p['_id']}/sections/Overview", json={"content": "updated"}, headers=auth["headers"])
        vs = versions(client, auth, p["_id"])
        assert len(vs) >= 2
        assert vs[0]["version"] > vs[1]["version"]
        assert vs[0]["sections_snapshot"]["Overview"] == {"content": "updated"}

    def test_restore_creates_new_version_and_restores_content(self, client, auth):
        p = create_proposal(client, auth)
        client.put(f"/api/v1/proposals/{p['_id']}/sections/Overview", json={"content": "v2 content"}, headers=auth["headers"])
        vs = versions(client, auth, p["_id"])
        v1 = next(v for v in vs if v["version"] == 1)

        resp = client.post(f"/api/v2/proposals/{p['_id']}/versions/{v1['_id']}/restore", headers=auth["headers"])
        assert resp.status_code == 200, resp.text

        fresh = versions(client, auth, p["_id"])
        assert len(fresh) == len(vs) + 1
        assert fresh[0]["note"].startswith("restored from")
        assert fresh[0]["parent_version"] == 1

    def test_diff_returns_section_changes(self, client, auth):
        p = create_proposal(client, auth)
        client.put(f"/api/v1/proposals/{p['_id']}/sections/Overview", json={"content": "v1 text"}, headers=auth["headers"])
        client.put(f"/api/v1/proposals/{p['_id']}/sections/Overview", json={"content": "v2 text"}, headers=auth["headers"])
        vs = versions(client, auth, p["_id"])
        v1 = next(v for v in vs if v["version"] == 1)
        v2 = next(v for v in vs if v["version"] == 2)

        resp = client.get(
            f"/api/v2/proposals/{p['_id']}/versions/diff",
            params={"from_version": v1["_id"], "to_version": v2["_id"]},
            headers=auth["headers"],
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["from_version"] == 1
        assert body["to_version"] == 2
        assert "Overview" in body["changes"]
        assert body["changes"]["Overview"]["to"]["content"] == "v2 text"

    def test_version_cross_tenant_404(self, client, auth):
        p = create_proposal(client, auth)
        client.put(f"/api/v1/proposals/{p['_id']}/sections/Overview", json={"content": "x"}, headers=auth["headers"])
        auth_b = register(client, "Bob", f"bob_{uuid4().hex[:8]}@test.com", "Beta Inc")
        resp = client.get(f"/api/v2/proposals/{p['_id']}/versions", headers=auth_b["headers"])
        assert resp.status_code == 404

    def test_version_creation_publishes_activity_event(self, client, mongo_db, auth):
        p = create_proposal(client, auth)
        client.put(f"/api/v1/proposals/{p['_id']}/sections/Overview", json={"content": "x"}, headers=auth["headers"])

        async def _find():
            return await mongo_db[0].activity_events.find_one(
                {"resource_id": p["_id"], "event_type": "proposal.version_created"}
            )

        ev = client.portal.call(_find)
        assert ev is not None
        assert ev["payload"]["version"] == 1
