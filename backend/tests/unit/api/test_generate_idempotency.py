"""Phase 3: durable generation - Idempotency-Key dedupe tests.

Exercises POST /api/v1/proposals/generate against the real stack (isolated
Mongo test DB, patched legacy model collections, Celery delay stubbed so no
real task is enqueued and no LLM work runs).
"""

from uuid import uuid4

import pytest
from bson import ObjectId
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
    monkeypatch.setattr("app.api.v1.proposals.generate_proposal_task", DummyCeleryTask())
    app = FastAPI()
    app.include_router(api_router)
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


def generate(client, auth, payload, key=None):
    headers = dict(auth["headers"])
    if key:
        headers["Idempotency-Key"] = key
    return client.post("/api/v1/proposals/generate", json=payload, headers=headers)


def count_docs(client, db, org_id):
    async def _count():
        return await db.generated_proposals.count_documents({"organization_id": org_id})

    return client.portal.call(_count)


class TestIdempotencyDedupe:
    def test_same_idempotency_key_returns_same_doc(self, client, mongo_db, auth):
        payload = {"client_input": "build a CRM for our sales team", "domain": "erp"}
        first = generate(client, auth, payload, key="key-123")
        second = generate(client, auth, payload, key="key-123")
        assert first.status_code == 200, first.text
        assert second.status_code == 200, second.text
        assert first.json()["_id"] == second.json()["_id"]
        assert count_docs(client, mongo_db[0], first.json()["organization_id"]) == 1

    def test_duplicate_request_hash_dedupes_without_key(self, client, mongo_db, auth):
        payload = {"client_input": "build a payroll system", "domain": "erp", "project_type": "web_app"}
        first = generate(client, auth, payload)
        second = generate(client, auth, payload)
        assert first.status_code == 200
        assert first.json()["_id"] == second.json()["_id"]
        assert count_docs(client, mongo_db[0], first.json()["organization_id"]) == 1

    def test_different_input_creates_new_doc(self, client, mongo_db, auth):
        first = generate(client, auth, {"client_input": "build a CRM"})
        second = generate(client, auth, {"client_input": "build an inventory system"})
        assert first.json()["_id"] != second.json()["_id"]
        assert count_docs(client, mongo_db[0], first.json()["organization_id"]) == 2

    def test_completed_generation_not_deduped(self, client, mongo_db, auth):
        payload = {"client_input": "build a fleet tracker"}
        first = generate(client, auth, payload, key="key-456")

        async def _finalize():
            await mongo_db[0].generated_proposals.update_one(
                {"_id": ObjectId(first.json()["_id"])},
                {"$set": {"status": "draft"}},
            )

        client.portal.call(_finalize)

        second = generate(client, auth, payload, key="key-456")
        assert second.json()["_id"] != first.json()["_id"]
        assert count_docs(client, mongo_db[0], first.json()["organization_id"]) == 2

    def test_duplicate_request_hash_from_different_tenant_not_deduped(self, client, mongo_db, auth):
        auth_b = register(client, "Bob", f"bob_{uuid4().hex[:8]}@test.com", "Beta Inc")
        payload = {"client_input": "identical input text"}
        doc_a = generate(client, auth, payload, key="shared-key")
        doc_b = generate(client, auth_b, payload, key="shared-key")
        assert doc_a.json()["_id"] != doc_b.json()["_id"]
        assert doc_a.json()["organization_id"] != doc_b.json()["organization_id"]


class TestEnqueueFailure:
    def test_broker_down_returns_503_and_cleans_up(self, client, mongo_db, auth, monkeypatch):
        monkeypatch.setattr("app.api.v1.proposals.generate_proposal_task", DummyCeleryTask(raise_on_delay=True))
        resp = generate(client, auth, {"client_input": "build a helpdesk"})
        assert resp.status_code == 503
        assert count_docs(client, mongo_db[0], auth["org_id"]) == 0

    def test_generate_enqueues_celery_task(self, client, mongo_db, auth, monkeypatch):
        task = DummyCeleryTask()
        monkeypatch.setattr("app.api.v1.proposals.generate_proposal_task", task)
        resp = generate(client, auth, {"client_input": "build a helpdesk"})
        assert resp.status_code == 200
        assert len(task.calls) == 1
        assert task.calls[0][0] == resp.json()["_id"]
