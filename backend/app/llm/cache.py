import hashlib
import logging
from typing import Optional

from app.infrastructure.cache.redis_cache import redis_cache
from app.config.settings import settings

logger = logging.getLogger("proposalcraft.llm_cache")


class LLMCache:
    def __init__(self):
        self._enabled = settings.ENABLE_LLM_CACHE

    def _make_key(self, prompt: str, model_key: str) -> str:
        raw = f"{prompt}:::{model_key}"
        return redis_cache._make_key("llm", raw)

    def get(self, prompt: str, model_key: str) -> Optional[str]:
        if not self._enabled:
            return None
        key = self._make_key(prompt, model_key)
        result = redis_cache.get(key)
        if result is not None:
            logger.debug("LLM cache HIT for key %s...", key[:28])
        return result

    def set(self, prompt: str, model_key: str, response: str, ttl_hours: int = 24) -> None:
        if not self._enabled:
            return
        key = self._make_key(prompt, model_key)
        redis_cache.set(key, response, ttl_seconds=ttl_hours * 3600)
        logger.debug("LLM cache SET for key %s...", key[:28])

    def clear(self) -> None:
        pass

    def delete(self, prompt: str, model_key: str) -> None:
        if not self._enabled:
            return
        key = self._make_key(prompt, model_key)
        redis_cache.delete(key)


llm_cache = LLMCache()
