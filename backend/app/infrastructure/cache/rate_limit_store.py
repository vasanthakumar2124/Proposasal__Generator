import logging
import time
import uuid
from collections import defaultdict

from app.config.settings import settings
from app.infrastructure.cache.redis_cache import redis_cache

logger = logging.getLogger("proposalcraft.cache.rate_limit")


class RateLimitStore:
    def __init__(self):
        self._memory: dict[str, list[float]] = defaultdict(list)

    def _client(self):
        return redis_cache._get_client()

    def _memory_clean(self, key: str, cutoff: float) -> None:
        self._memory[key] = [t for t in self._memory[key] if t > cutoff]

    def add(self, key: str, now: float, window: int) -> int:
        client = self._client()
        if client:
            try:
                redis_key = redis_cache._make_key("ratelimit", key)
                client.zremrangebyscore(redis_key, 0, now - window)
                client.zadd(redis_key, {f"{now}:{uuid.uuid4().hex[:8]}": now})
                client.expire(redis_key, window * 2)
                return int(client.zcard(redis_key))
            except Exception as e:
                logger.debug("Rate limit store Redis failed: %s", e)
        self._memory_clean(key, now - window)
        self._memory[key].append(now)
        return len(self._memory[key])


rate_limit_store = RateLimitStore()
