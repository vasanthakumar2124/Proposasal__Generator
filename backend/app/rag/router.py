import logging
from typing import List

from fastapi import APIRouter, HTTPException

from app.rag.schemas import SearchQuery, SearchResult, IngestDocument, CollectionInfo
from app.rag.service import qdrant_service
from app.rag.ingest import ingest_pipeline

logger = logging.getLogger("proposalcraft.rag.router")

router = APIRouter(prefix="/rag", tags=["rag"])


@router.get("/collections", response_model=List[CollectionInfo])
async def list_collections():
    try:
        return qdrant_service.get_collections()
    except Exception as e:
        logger.error("Failed to list collections: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[SearchResult])
async def search_documents(query: SearchQuery):
    try:
        return qdrant_service.search(
            query=query.query,
            collection_name=query.collection_name,
            top_k=query.top_k,
            score_threshold=query.score_threshold,
        )
    except Exception as e:
        logger.error("Search failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", response_model=dict)
async def ingest_document(document: IngestDocument):
    try:
        point_ids = ingest_pipeline.ingest_text(document)
        return {"ingested": len(point_ids), "point_ids": point_ids}
    except Exception as e:
        logger.error("Ingest failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seed", response_model=dict)
async def seed_knowledge():
    try:
        ingest_pipeline.seed_default_knowledge()
        return {"status": "ok", "message": "Default knowledge seeded"}
    except Exception as e:
        logger.error("Seed failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{collection_name}/{point_id}")
async def delete_document(collection_name: str, point_id: str):
    try:
        qdrant_service.delete_document(collection_name, point_id)
        return {"deleted": True}
    except Exception as e:
        logger.error("Delete failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
