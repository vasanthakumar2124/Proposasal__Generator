import logging
from typing import Optional
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter

from app.config.settings import settings
from app.llm.embeddings import embedding_service
from app.rag.schemas import SearchResult, CollectionInfo

logger = logging.getLogger("proposalcraft.qdrant")

QDRANT_COLLECTIONS = {
    "proposal_examples": "Proposal examples for few-shot learning",
    "industry_knowledge": "Domain-specific compliance, trends, stakeholders",
    "technology_knowledge": "Tech stack patterns and best practices",
    "pricing_data": "Pricing benchmarks and rate cards",
    "case_studies": "Relevant case studies and success stories",
    "best_practices": "Development and project management best practices",
    "automation_patterns": "Automation and integration patterns",
    "compliance_standards": "Regulatory and compliance standards per industry",
}


def scoped_collection_name(base: str, org_id: Optional[str]) -> str:
    """Namespace a collection by organization, derived server-side from the
    authenticated org_id — never from client-supplied input. With org_id=None
    the base name is returned unchanged (global built-in knowledge)."""
    if not org_id:
        return base
    prefix = f"org_{org_id}_"
    if base.startswith(prefix):
        return base
    return f"{prefix}{base}"


class QdrantService:
    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self._initialized = False

    def _get_client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(
                url=settings.QDRANT_URL or None,
                api_key=settings.QDRANT_API_KEY or None,
                location=":memory:" if not settings.QDRANT_URL else None,
                prefer_grpc=False,
                check_compatibility=False,
            )
        return self._client

    def initialize(self) -> None:
        if self._initialized:
            return
        client = self._get_client()
        dims = embedding_service.dimensions
        existing = {c.name for c in client.get_collections().collections}
        for name in QDRANT_COLLECTIONS:
            if name not in existing:
                client.create_collection(
                    collection_name=name,
                    vectors_config=VectorParams(size=dims, distance=Distance.COSINE),
                )
                logger.info("Created Qdrant collection: %s (%dd)", name, dims)
        self._initialized = True

    def _ensure_collection(self, collection_name: str) -> None:
        client = self._get_client()
        existing = {c.name for c in client.get_collections().collections}
        if collection_name not in existing:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=embedding_service.dimensions,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("Created Qdrant collection: %s", collection_name)

    def upsert(self, collection_name: str, points: list[PointStruct]) -> int:
        self._ensure_collection(collection_name)
        client = self._get_client()
        client.upsert(collection_name=collection_name, points=points)
        return len(points)

    def insert_document(
        self,
        collection_name: str,
        content: str,
        metadata: dict = None,
        org_id: Optional[str] = None,
    ) -> str:
        collection_name = scoped_collection_name(collection_name, org_id)
        point_id = str(uuid4())
        vector = embedding_service.embed_query(content)
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload={"content": content, **(metadata or {})},
        )
        self.upsert(collection_name, [point])
        return point_id

    def search(
        self,
        query: str,
        collection_name: str = "industry_knowledge",
        top_k: int = 5,
        score_threshold: float = 0.0,
        payload_filter: Optional[Filter] = None,
        org_id: Optional[str] = None,
    ) -> list[SearchResult]:
        collection_name = scoped_collection_name(collection_name, org_id)
        client = self._get_client()
        existing = {c.name for c in client.get_collections().collections}
        if collection_name not in existing:
            return []
        vector = embedding_service.embed_query(query)
        hits = client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=payload_filter,
        )
        return [
            SearchResult(
                content=h.payload.get("content", ""),
                score=h.score,
                metadata={k: v for k, v in h.payload.items() if k != "content"},
                collection_name=collection_name,
            )
            for h in hits
        ]

    def delete_document(
        self, collection_name: str, point_id: str, org_id: Optional[str] = None
    ) -> bool:
        collection_name = scoped_collection_name(collection_name, org_id)
        client = self._get_client()
        client.delete(collection_name=collection_name, points_selector=[point_id])
        return True

    def get_collections(self, org_id: Optional[str] = None) -> list[CollectionInfo]:
        client = self._get_client()
        collections = client.get_collections().collections
        result = []
        prefix = f"org_{org_id}_" if org_id else ""
        for c in collections:
            name = c.name
            if prefix and not name.startswith(prefix):
                continue
            if prefix:
                name = name[len(prefix):]
            info = client.get_collection(c.name)
            result.append(CollectionInfo(
                name=name,
                vectors_count=info.vectors_count or 0,
                dimensions=info.config.params.vectors.size,
            ))
        return result

    def count_documents(
        self, collection_name: str, org_id: Optional[str] = None
    ) -> int:
        collection_name = scoped_collection_name(collection_name, org_id)
        client = self._get_client()
        info = client.get_collection(collection_name)
        return info.vectors_count or 0


qdrant_service = QdrantService()
