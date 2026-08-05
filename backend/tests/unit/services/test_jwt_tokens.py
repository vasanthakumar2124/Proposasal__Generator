import pytest

from app.infrastructure.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)
from app.domain.exceptions import TokenExpiredError, TokenInvalidError


class TestJwtTokens:
    def test_access_token_roundtrip(self):
        token = create_access_token("user1", {"org_id": "org1"})
        payload = verify_access_token(token)
        assert payload["sub"] == "user1"
        assert payload["type"] == "access"

    def test_refresh_token_roundtrip(self):
        token = create_refresh_token("user1")
        payload = verify_refresh_token(token)
        assert payload["sub"] == "user1"
        assert payload["type"] == "refresh"

    def test_access_token_rejected_as_refresh(self):
        # Regression: refresh_token() used verify_access_token, which rejects
        # type=refresh — the /auth/refresh endpoint always 401'd and forced
        # users to re-login every 15 minutes.
        access = create_access_token("user1")
        with pytest.raises(TokenInvalidError):
            verify_refresh_token(access)

    def test_refresh_token_rejected_as_access(self):
        refresh = create_refresh_token("user1")
        with pytest.raises(TokenInvalidError):
            verify_access_token(refresh)

    def test_garbage_token_invalid(self):
        with pytest.raises(TokenInvalidError):
            verify_refresh_token("not.a.jwt")
