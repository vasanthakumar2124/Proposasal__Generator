import asyncio

import pytest

from app.domain.entities.user import User
from app.domain.entities.organization import Organization
from app.domain.exceptions import InvalidCredentialsError
from app.infrastructure.auth.refresh_store import hash_refresh_token
from app.infrastructure.auth.password import hash_password
from app.services.auth_service import AuthService


class FakeUserRepo:
    def __init__(self, user):
        self.user = user

    async def get_by_email(self, email):
        return self.user if self.user.email == email else None

    async def get_by_id(self, user_id):
        return self.user if self.user.id == user_id else None

    async def create(self, user):
        return user

    async def update(self, user):
        return user


class FakeOrgRepo:
    def __init__(self, org):
        self.org = org

    async def get_by_id(self, org_id):
        return self.org if self.org.id == org_id else None

    async def create(self, org):
        return org


class FakeStore:
    def __init__(self):
        self.records = {}
        self.revoke_all_calls = 0

    async def store(self, user_id, org_id, token, expires_at, meta=None):
        self.records[hash_refresh_token(token)] = {
            "token_hash": hash_refresh_token(token),
            "user_id": user_id,
            "organization_id": org_id,
            "expires_at": expires_at,
            "revoked": False,
            "meta": meta or {},
        }

    async def find(self, token):
        return self.records.get(hash_refresh_token(token))

    async def revoke(self, token):
        record = self.records.get(hash_refresh_token(token))
        if record:
            record["revoked"] = True

    async def revoke_all_for_user(self, user_id):
        self.revoke_all_calls += 1
        count = 0
        for record in self.records.values():
            if record["user_id"] == user_id and not record["revoked"]:
                record["revoked"] = True
                count += 1
        return count


@pytest.fixture
def auth_ctx(monkeypatch):
    user = User(
        _id="u1",
        email="test@example.com",
        password_hash=hash_password("hashed"),
        name="Test User",
        organization_id="org1",
    )
    org = Organization(_id="org1", name="Acme", slug="acme")
    store = FakeStore()

    async def noop_audit(**kwargs):
        return None

    monkeypatch.setattr("app.services.auth_service.refresh_token_store", store)
    monkeypatch.setattr("app.services.auth_service.create_audit_log", noop_audit)
    service = AuthService(user_repo=FakeUserRepo(user), org_repo=FakeOrgRepo(org))
    return service, store


class TestRefreshRotation:
    def test_login_stores_refresh_token(self, auth_ctx):
        service, store = auth_ctx
        _, _, _, refresh = asyncio.run(service.login("test@example.com", "hashed"))
        assert hash_refresh_token(refresh) in store.records
        assert store.records[hash_refresh_token(refresh)]["revoked"] is False

    def test_refresh_rotates_old_for_new(self, auth_ctx):
        service, store = auth_ctx
        _, _, _, refresh = asyncio.run(service.login("test@example.com", "hashed"))

        access, new_refresh = asyncio.run(service.refresh_token(refresh))

        assert access
        assert new_refresh != refresh
        assert store.records[hash_refresh_token(refresh)]["revoked"] is True
        assert hash_refresh_token(new_refresh) in store.records
        assert store.records[hash_refresh_token(new_refresh)]["revoked"] is False

    def test_reuse_detection_revokes_all_sessions(self, auth_ctx):
        service, store = auth_ctx
        _, _, _, refresh = asyncio.run(service.login("test@example.com", "hashed"))
        _, new_refresh = asyncio.run(service.refresh_token(refresh))

        with pytest.raises(InvalidCredentialsError):
            asyncio.run(service.refresh_token(refresh))

        assert store.revoke_all_calls == 1
        assert store.records[hash_refresh_token(new_refresh)]["revoked"] is True

    def test_revoked_token_rejected(self, auth_ctx):
        service, store = auth_ctx
        _, _, _, refresh = asyncio.run(service.login("test@example.com", "hashed"))
        asyncio.run(service.logout(refresh))

        with pytest.raises(InvalidCredentialsError):
            asyncio.run(service.refresh_token(refresh))

    def test_garbage_refresh_token_rejected(self, auth_ctx):
        service, _ = auth_ctx
        with pytest.raises(InvalidCredentialsError):
            asyncio.run(service.refresh_token("not.a.jwt"))

    def test_logout_without_token_is_noop(self, auth_ctx):
        service, _ = auth_ctx
        assert asyncio.run(service.logout()) is None
