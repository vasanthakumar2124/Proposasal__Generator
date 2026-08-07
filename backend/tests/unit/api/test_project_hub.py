"""Phase 4: Project Hub (v2) tests.

Exercises /api/v2/projects/{id}/hub (aggregation), PATCH hub fields, and
POST /{id}/generate (project-scoped generation + idempotency) against the
real stack (isolated Mongo test DB, Celery delay stubbed).
"""

from datetime import datetime, timezone
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
    monkeypatch.setattr("app.billing.service.subscription_collection", db.subscriptions)
    monkeypatch.setattr("app.models.generated_proposal_model.generated_proposal_collection", db.generated_proposals)
    monkeypatch.setattr("app.services.generated_proposal_service.generated_proposal_collection", db.generated_proposals)
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


def create_project(client, auth, name):
    resp = client.post("/api/v1/projects", json={"name": name}, headers=auth["headers"])
    assert resp.status_code == 201, resp.text
    return resp.json()


def hub_get(client, auth, project_id):
    return client.get(f"/api/v2/projects/{project_id}/hub", headers=auth["headers"])


class TestHubAggregation:
    def test_hub_returns_project_proposals_and_activity(self, client, mongo_db, auth):
        project = create_project(client, auth, "Fleet Tracker")
        async def _seed():
            await mongo_db[0].generated_proposals.insert_one(
                {
                    "_id": ObjectId(),
                    "title": "Fleet Tracking Proposal",
                    "organization_id": auth["org_id"],
                    "project_id": project["_id"],
                    "proposal_id": "PROP-SEED-1",
                    "status": "draft",
                    "created_at": datetime.now(timezone.utc),
                }
            )
        client.portal.call(_seed)

        resp = hub_get(client, auth, project["_id"])
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["project"]["_id"] == project["_id"]
        assert body["project"]["goal"] == ""
        assert body["project"]["key_features"] == []
        assert len(body["proposals"]) == 1
        assert body["proposals"][0]["title"] == "Fleet Tracking Proposal"
        assert any(ev["event_type"] == "project.created" for ev in body["activity"])

    def test_hub_cross_tenant_404(self, client, auth):
        project = create_project(client, auth, "Secret Project")
        auth_b = register(client, "Bob", f"bob_{uuid4().hex[:8]}@test.com", "Beta Inc")
        assert hub_get(client, auth_b, project["_id"]).status_code == 404


class TestHubUpdate:
    def test_patch_updates_hub_fields(self, client, auth):
        project = create_project(client, auth, "CRM Build")
        resp = client.patch(
            f"/api/v2/projects/{project['_id']}",
            json={
                "goal": "Unify sales data",
                "budget": 45000,
                "currency": "EUR",
                "timeline": "4 months",
                "key_features": ["Dashboards", "API"],
                "notes": "Priority client",
                "status": "active",
            },
            headers=auth["headers"],
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["goal"] == "Unify sales data"
        assert body["budget"] == 45000
        assert body["currency"] == "EUR"
        assert body["key_features"] == ["Dashboards", "API"]
        assert body["status"] == "active"

    def test_patch_cross_tenant_404_no_mutation(self, client, mongo_db, auth):
        project = create_project(client, auth, "Internal Tool")
        auth_b = register(client, "Bob", f"bob_{uuid4().hex[:8]}@test.com", "Beta Inc")
        resp = client.patch(
            f"/api/v2/projects/{project['_id']}",
            json={"goal": "hijacked"},
            headers=auth_b["headers"],
        )
        assert resp.status_code == 404

        async def _check():
            doc = await mongo_db[0].projects.find_one({"_id": ObjectId(project["_id"])})
            return doc.get("goal", "")

        assert client.portal.call(_check) == ""


class TestHubGenerate:
    def test_generate_creates_doc_with_project_id_and_enqueues(self, client, mongo_db, auth, monkeypatch):
        task = DummyCeleryTask()
        monkeypatch.setattr("app.api.v2.projects.generate_proposal_task", task)
        project = create_project(client, auth, "Payroll System")

        resp = client.post(
            f"/api/v2/projects/{project['_id']}/generate",
            json={"client_input": "Build a payroll system", "domain": "erp"},
            headers=auth["headers"],
        )
        assert resp.status_code == 200, resp.text
        doc = resp.json()
        assert doc["project_id"] == project["_id"]
        assert doc["status"] == "processing"
        assert len(task.calls) == 1
        assert task.calls[0][0] == doc["_id"]

        async def _check():
            return await mongo_db[0].generated_proposals.find_one({"_id": ObjectId(doc["_id"])})

        stored = client.portal.call(_check)
        assert stored["project_id"] == project["_id"]

    def test_same_project_same_key_dedupes(self, client, mongo_db, auth):
        project = create_project(client, auth, "Inventory App")
        headers = {**auth["headers"], "Idempotency-Key": "hub-key-1"}
        first = client.post(
            f"/api/v2/projects/{project['_id']}/generate",
            json={"client_input": "Build inventory app"},
            headers=headers,
        )
        second = client.post(
            f"/api/v2/projects/{project['_id']}/generate",
            json={"client_input": "Build inventory app"},
            headers=headers,
        )
        assert first.json()["_id"] == second.json()["_id"]

        async def _count():
            return await mongo_db[0].generated_proposals.count_documents(
                {"organization_id": auth["org_id"], "project_id": project["_id"]}
            )

        assert client.portal.call(_count) == 1

    def test_same_key_different_project_not_deduped(self, client, mongo_db, auth):
        project_a = create_project(client, auth, "App A")
        project_b = create_project(client, auth, "App B")
        payload = {"client_input": "identical input"}
        headers = {**auth["headers"], "Idempotency-Key": "shared-hub-key"}
        doc_a = client.post(f"/api/v2/projects/{project_a['_id']}/generate", json=payload, headers=headers)
        doc_b = client.post(f"/api/v2/projects/{project_b['_id']}/generate", json=payload, headers=headers)
        assert doc_a.json()["_id"] != doc_b.json()["_id"]

        async def _count():
            return await mongo_db[0].generated_proposals.count_documents(
                {"organization_id": auth["org_id"], "status": "processing"}
            )

        assert client.portal.call(_count) == 2

    def test_cross_tenant_project_generate_404(self, client, auth):
        project = create_project(client, auth, "Confidential")
        auth_b = register(client, "Bob", f"bob_{uuid4().hex[:8]}@test.com", "Beta Inc")
        resp = client.post(
            f"/api/v2/projects/{project['_id']}/generate",
            json={"client_input": "steal scope"},
            headers=auth_b["headers"],
        )
        assert resp.status_code == 404

    def test_broker_down_returns_503_and_cleans_up(self, client, mongo_db, auth, monkeypatch):
        monkeypatch.setattr("app.api.v2.projects.generate_proposal_task", DummyCeleryTask(raise_on_delay=True))
        project = create_project(client, auth, "Helpdesk")
        resp = client.post(
            f"/api/v2/projects/{project['_id']}/generate",
            json={"client_input": "Build a helpdesk"},
            headers=auth["headers"],
        )
        assert resp.status_code == 503

        async def _count():
            return await mongo_db[0].generated_proposals.count_documents(
                {"organization_id": auth["org_id"]}
            )

        assert client.portal.call(_count) == 0

    def test_empty_client_input_400(self, client, auth):
        project = create_project(client, auth, "No Scope")
        resp = client.post(
            f"/api/v2/projects/{project['_id']}/generate",
            json={"client_input": "   "},
            headers=auth["headers"],
        )
        assert resp.status_code == 400
