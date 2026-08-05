from unittest.mock import patch, MagicMock
import pytest

from app.config.settings import settings


class TestQdrantServiceMocked:
    def test_collections_defined(self):
        from app.rag.service import QDRANT_COLLECTIONS
        assert len(QDRANT_COLLECTIONS) == 8
        assert "industry_knowledge" in QDRANT_COLLECTIONS

    def test_insert_and_search_mocked(self, monkeypatch):
        monkeypatch.setattr(settings, "QDRANT_URL", "")
        monkeypatch.setattr(settings, "QDRANT_API_KEY", "")
        with patch("app.rag.service.embedding_service") as mock_embed:
            mock_embed.dimensions = 4
            mock_embed.embed_query.return_value = [0.1, 0.2, 0.3, 0.4]

            from app.rag.service import QdrantService
            service = QdrantService()
            service._client = None
            service._initialized = False
            service.initialize()

            pid = service.insert_document(
                "best_practices",
                "Test-driven development reduces bugs.",
                {"category": "testing"},
            )
            assert pid is not None

            results = service.search("test driven", "best_practices")
            assert len(results) >= 1
