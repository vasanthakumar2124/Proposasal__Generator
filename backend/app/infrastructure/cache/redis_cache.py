import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app.config.settings import settings

logger = logging.getLogger("proposalcraft.cache.redis")


class RedisCache:
    def __init__(self):
        self._client = None
        self._memory: dict[str, tuple[Any, datetime]] = {}
        self._enabled = True

    def _get_client(self):
        if self._client is None and settings.REDIS_URL:
            try:
                import redis as sync_redis
                self._client = sync_redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                    protocol=2,
                )
                self._client.ping()
                logger.info("Redis cache connected")
            except Exception as e:
                logger.warning("Redis unavailable, using memory cache: %s", e)
                self._client = None
        return self._client

    def get(self, key: str) -> Optional[Any]:
        client = self._get_client()
        if client:
            try:
                val = client.get(key)
                if val:
                    return json.loads(val)
            except Exception as e:
                logger.debug("Redis get failed: %s", e)
        return self._memory_get(key)

    def set(self, key: str, value: Any, ttl_seconds: int = 86400) -> None:
        client = self._get_client()
        if client:
            try:
                client.setex(key, ttl_seconds, json.dumps(value))
                return
            except Exception as e:
                logger.debug("Redis set failed: %s", e)
        self._memory_set(key, value, ttl_seconds)

    def delete(self, key: str) -> None:
        client = self._get_client()
        if client:
            try:
                client.delete(key)
                return
            except Exception:
                pass
        self._memory.pop(key, None)

    def clear(self) -> None:
        client = self._get_client()
        if client:
            try:
                client.flushdb()
                return
            except Exception:
                pass
        self._memory.clear()

    def _make_key(self, prefix: str, *parts: str) -> str:
        raw = ":".join(str(p) for p in parts)
        return f"proposalcraft:{prefix}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()}"

    def _memory_get(self, key: str) -> Optional[Any]:
        entry = self._memory.get(key)
        if entry:
            value, expires = entry
            if datetime.now(timezone.utc) < expires:
                return value
            del self._memory[key]
        return None

    def _memory_set(self, key: str, value: Any, ttl_seconds: int) -> None:
        expires = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        self._memory[key] = (value, expires)


redis_cache = RedisCache()


def get_redis_cache() -> RedisCache:
    return redis_cache
