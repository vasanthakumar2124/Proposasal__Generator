import hashlib
from datetime import datetime, timezone
from typing import Optional

from app.infrastructure.database.mongodb import get_database


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class RefreshTokenStore:
    async def store(
        self,
        user_id: str,
        org_id: str,
        token: str,
        expires_at: datetime,
        meta: Optional[dict] = None,
    ) -> None:
        db = await get_database()
        await db.refresh_tokens.insert_one(
            {
                "token_hash": hash_refresh_token(token),
                "user_id": user_id,
                "organization_id": org_id,
                "expires_at": expires_at,
                "revoked": False,
                "replaced_by": None,
                "meta": meta or {},
                "created_at": datetime.now(timezone.utc),
            }
        )

    async def find(self, token: str) -> Optional[dict]:
        db = await get_database()
        return await db.refresh_tokens.find_one({"token_hash": hash_refresh_token(token)})

    async def revoke(self, token: str) -> None:
        db = await get_database()
        await db.refresh_tokens.update_one(
            {"token_hash": hash_refresh_token(token)},
            {"$set": {"revoked": True}},
        )

    async def revoke_all_for_user(self, user_id: str) -> int:
        db = await get_database()
        result = await db.refresh_tokens.update_many(
            {"user_id": user_id, "revoked": False},
            {"$set": {"revoked": True}},
        )
        return result.modified_count


refresh_token_store = RefreshTokenStore()
