from qdrant_client import QdrantClient
from app.config.settings import settings


def get_qdrant_client():
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        check_compatibility=False,
    )
    return client
