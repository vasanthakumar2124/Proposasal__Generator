"""Phase 2c: cross-tenant isolation tests for every org-scoped surface.

Uses the real v1 API stack (real services, real Mongo on an isolated test
database, in-memory Qdrant) with two real registered organizations.

Audit logs are deliberately excluded: they are write-only (app.infrastructure.
log.audit.create_audit_log) with no read API, so there is no cross-tenant read
surface to test.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from app.api.v1.api import api_router
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
    app = FastAPI()
    app.include_router(api_router)
    with TestClient(app) as c:
        c.portal.call(mongodb.ensure_indexes)
        yield c

        async def _drop():
            await db.client.drop_database(db_name)

        c.portal.call(_drop)


def register(client, name, email, company):
    resp = client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": "password123", "company_name": company},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    return {
        "token": data["access_token"],
        "user": data["user"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
    }


@pytest.fixture
def org_a(client):
    return register(client, "Alice", f"alice_{uuid4().hex[:8]}@test.com", "OrgA Corp")


@pytest.fixture
def org_b(client):
    return register(client, "Bob", f"bob_{uuid4().hex[:8]}@test.com", "OrgB Corp")


class TestCrudIsolation:
    def test_org_b_cannot_read_org_a_entities(self, client, org_a, org_b):
        h_a, h_b = org_a["headers"], org_b["headers"]

        cid = client.post("/api/v1/clients", json={"name": "Acme", "email": "a@acme.com"}, headers=h_a).json()["_id"]
        wid = client.post("/api/v1/workspaces", json={"name": "Sales Workspace"}, headers=h_a).json()["_id"]
        pid = client.post("/api/v1/projects", json={"name": "CRM Rollout", "workspace_id": wid}, headers=h_a).json()["_id"]
        prid = client.post("/api/v1/proposals", json={"title": "CRM Proposal", "project_id": pid}, headers=h_a).json()["_id"]

        for path in (f"/api/v1/clients/{cid}", f"/api/v1/workspaces/{wid}",
                     f"/api/v1/projects/{pid}", f"/api/v1/proposals/{prid}"):
            resp = client.get(path, headers=h_b)
            assert resp.status_code == 404, f"B read {path}: {resp.status_code}"

        assert client.get("/api/v1/clients", headers=h_b).json()["total"] == 0
        assert client.get("/api/v1/workspaces", headers=h_b).json()["total"] == 0
        assert client.get("/api/v1/projects", headers=h_b).json()["total"] == 0
        assert client.get("/api/v1/proposals", headers=h_b).json()["total"] == 0

        assert client.get("/api/v1/clients", headers=h_a).json()["total"] == 1
        assert client.get("/api/v1/proposals", headers=h_a).json()["total"] == 1

    def test_org_b_cannot_mutate_org_a_entities(self, client, org_a, org_b):
        h_a, h_b = org_a["headers"], org_b["headers"]

        cid = client.post("/api/v1/clients", json={"name": "Acme"}, headers=h_a).json()["_id"]
        wid = client.post("/api/v1/workspaces", json={"name": "Sales"}, headers=h_a).json()["_id"]
        pid = client.post("/api/v1/projects", json={"name": "CRM Rollout"}, headers=h_a).json()["_id"]
        prid = client.post("/api/v1/proposals", json={"title": "CRM Proposal"}, headers=h_a).json()["_id"]

        assert client.put(f"/api/v1/clients/{cid}", json={"name": "Hacked"}, headers=h_b).status_code == 404
        assert client.delete(f"/api/v1/clients/{cid}", headers=h_b).status_code == 404
        assert client.put(f"/api/v1/workspaces/{wid}", json={"name": "Hacked"}, headers=h_b).status_code == 404
        assert client.delete(f"/api/v1/workspaces/{wid}", headers=h_b).status_code == 404
        assert client.put(f"/api/v1/projects/{pid}", json={"name": "Hacked"}, headers=h_b).status_code == 404
        assert client.delete(f"/api/v1/projects/{pid}", headers=h_b).status_code == 404
        assert client.put(f"/api/v1/proposals/{prid}", json={"title": "Hacked"}, headers=h_b).status_code == 404
        assert client.delete(f"/api/v1/proposals/{prid}", headers=h_b).status_code == 404

        assert client.get(f"/api/v1/clients/{cid}", headers=h_a).json()["name"] == "Acme"
        assert client.get(f"/api/v1/proposals/{prid}", headers=h_a).json()["title"] == "CRM Proposal"

    def test_org_b_cannot_read_org_a_organization(self, client, org_a, org_b):
        h_b = org_b["headers"]
        org_a_id = org_a["user"]["organization_id"]
        resp = client.get(f"/api/v1/orgs/{org_a_id}", headers=h_b)
        assert resp.status_code == 403
        resp = client.put(f"/api/v1/orgs/{org_a_id}", json={"name": "Hacked"}, headers=h_b)
        assert resp.status_code == 403

    def test_org_b_cannot_see_org_a_members(self, client, org_a, org_b):
        h_a, h_b = org_a["headers"], org_b["headers"]
        invite = client.post(
            "/api/v1/members",
            json={"email": f"carl_{uuid4().hex[:8]}@test.com", "role": "viewer"},
            headers=h_a,
        )
        assert invite.status_code == 201, invite.text

        names_a = {m["email"] for m in client.get("/api/v1/members", headers=h_a).json()["items"]}
        names_b = {m["email"] for m in client.get("/api/v1/members", headers=h_b).json()["items"]}
        assert invite.json()["email"] in names_a
        assert invite.json()["email"] not in names_b


class TestTelemetryIsolation:
    def test_org_b_activity_feed_excludes_org_a_events(self, client, mongo_db, org_a, org_b):
        h_a, h_b = org_a["headers"], org_b["headers"]
        client.post("/api/v1/proposals", json={"title": "A private proposal"}, headers=h_a)
        client.post("/api/v1/clients", json={"name": "Acme"}, headers=h_a)

        insert_docs(client, mongo_db[0], "activity_events", [{
            "organization_id": org_a["user"]["organization_id"],
            "event_type": "proposal.created",
            "resource_type": "proposal",
            "resource_id": "prop-xyz",
            "actor_id": "user-xyz",
            "payload": {"title": "injected org-a event"},
        }])

        feed_a = client.get("/api/v1/activity", headers=h_a).json()["items"]
        feed_b = client.get("/api/v1/activity", headers=h_b).json()["items"]
        ids_a = {i["_id"] for i in feed_a}
        ids_b = {i["_id"] for i in feed_b}
        assert "prop-xyz" in {i.get("resource_id") for i in feed_a}
        assert ids_b.isdisjoint(ids_a)

    def test_org_b_usage_reflects_only_org_b(self, client, mongo_db, org_a, org_b):
        h_a, h_b = org_a["headers"], org_b["headers"]
        from datetime import datetime, timezone

        period = datetime.now(timezone.utc).strftime("%Y-%m")
        upsert_usage(client, mongo_db[0], {
            "organization_id": org_a["user"]["organization_id"],
            "period": period,
            "llm_calls": 999,
            "input_tokens": 123456,
            "output_tokens": 654321,
        })

        usage_a = client.get("/api/v1/billing/usage", headers=h_a).json()
        usage_b = client.get("/api/v1/billing/usage", headers=h_b).json()
        assert usage_a["usage"]["llm_calls"] == 999
        assert usage_a["usage"]["input_tokens"] == 123456
        assert usage_b["usage"]["llm_calls"] == 0
        assert usage_b["usage"]["input_tokens"] == 0


def upsert_usage(client, db, doc):
    from datetime import datetime, timezone

    async def _upsert():
        await db.usage.update_one(
            {"organization_id": doc["organization_id"], "period": doc["period"]},
            {"$set": {k: v for k, v in doc.items() if k not in ("organization_id", "period")}},
            upsert=True,
        )

    client.portal.call(_upsert)


def insert_docs(client, db, collection, docs):
    from datetime import datetime, timezone

    async def _insert():
        now = datetime.now(timezone.utc)
        for doc in docs:
            doc = dict(doc)
            doc.setdefault("occurred_at", now)
            doc.setdefault("created_at", now)
            await db[collection].insert_one(doc)

    client.portal.call(_insert)
