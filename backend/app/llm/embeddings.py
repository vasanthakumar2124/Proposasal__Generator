import hashlib
import logging
from dataclasses import dataclass
from typing import Optional

from app.config.settings import settings
from app.infrastructure.cache.redis_cache import redis_cache

logger = logging.getLogger("proposalcraft.embeddings")


@dataclass
class EmbeddingConfig:
    provider: str
    model: str
    dimensions: int
    cost_per_1k_tokens: float = 0.0


EMBEDDING_REGISTRY: list[EmbeddingConfig] = [
    EmbeddingConfig("sentence_transformers", "all-MiniLM-L6-v2", 384, 0.0),
    EmbeddingConfig("sentence_transformers", "all-mpnet-base-v2", 768, 0.0),
    EmbeddingConfig("openai", "text-embedding-3-small", 1536, 0.00002),
    EmbeddingConfig("openai", "text-embedding-3-large", 3072, 0.00013),
]


class EmbeddingService:
    def __init__(self):
        self._model = None
        self._enabled = settings.ENABLE_EMBEDDING_CACHE
        self._config = self._resolve_config()

    def _resolve_config(self) -> EmbeddingConfig:
        provider = settings.EMBEDDING_PROVIDER
        for cfg in EMBEDDING_REGISTRY:
            if cfg.provider == provider:
                return cfg
        return EMBEDDING_REGISTRY[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        cache_key = self._cache_key(text)
        if self._enabled:
            cached = redis_cache.get(cache_key)
            if cached is not None:
                return cached

        if self._config.provider == "sentence_transformers":
            vector = self._embed_sentence_transformers(text)
        elif self._config.provider == "openai":
            vector = self._embed_openai(text)
        else:
            vector = self._embed_sentence_transformers(text)

        if self._enabled:
            redis_cache.set(cache_key, vector, ttl_seconds=86400)
        return vector

    def _cache_key(self, text: str) -> str:
        raw = f"{self._config.provider}:{self._config.model}:{text}"
        return redis_cache._make_key("embed", raw)

    def _embed_sentence_transformers(self, text: str) -> list[float]:
        from sentence_transformers import SentenceTransformer
        if self._model is None:
            self._model = SentenceTransformer(self._config.model)
        vec = self._model.encode(text).tolist()
        return vec

    def _embed_openai(self, text: str) -> list[float]:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        resp = client.embeddings.create(model=self._config.model, input=text)
        return resp.data[0].embedding

    @property
    def dimensions(self) -> int:
        return self._config.dimensions


embedding_service = EmbeddingService()
