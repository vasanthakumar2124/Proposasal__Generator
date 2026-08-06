import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from app.domain.entities.user import User
from app.api.deps import require_permission, get_current_org
from app.rag.schemas import SearchQuery, SearchResult, IngestDocument, CollectionInfo
from app.rag.service import qdrant_service
from app.rag.ingest import ingest_pipeline
from app.rag.loader import load_pdf, load_docx, load_text_file
from app.services.upload_service import upload_service

logger = logging.getLogger("proposalcraft.rag.router")

router = APIRouter(tags=["rag"])


@router.post("/ingest/file", response_model=dict)
async def ingest_file(
    file: UploadFile = File(...),
    collection_name: str = Form("industry_knowledge"),
    user: User = Depends(require_permission("knowledge:create")),
    org_id: str = Depends(get_current_org),
):
    try:
        path, ext = await upload_service.save(file, org_id)
        if ext == ".pdf":
            docs = load_pdf(str(path))
        elif ext == ".docx":
            docs = load_docx(str(path))
        else:
            docs = load_text_file(str(path))
        content = "\n\n".join(d.page_content if hasattr(d, "page_content") else d.get("page_content", "") for d in docs)
        if not content.strip():
            raise HTTPException(status_code=422, detail="No extractable text found in file")
        point_ids = ingest_pipeline.ingest_text(
            IngestDocument(content=content, collection_name=collection_name),
            org_id=org_id,
        )
        return {"ingested": len(point_ids), "point_ids": point_ids, "source": file.filename}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("File ingest failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections", response_model=List[CollectionInfo])
async def list_collections(
    user: User = Depends(require_permission("knowledge:read")),
    org_id: str = Depends(get_current_org),
):
    try:
        return qdrant_service.get_collections(org_id=org_id)
    except Exception as e:
        logger.error("Failed to list collections: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[SearchResult])
async def search_documents(
    query: SearchQuery,
    user: User = Depends(require_permission("knowledge:read")),
    org_id: str = Depends(get_current_org),
):
    try:
        return qdrant_service.search(
            query=query.query,
            collection_name=query.collection_name,
            top_k=query.top_k,
            score_threshold=query.score_threshold,
            org_id=org_id,
        )
    except Exception as e:
        logger.error("Search failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest", response_model=dict)
async def ingest_document(
    document: IngestDocument,
    user: User = Depends(require_permission("knowledge:create")),
    org_id: str = Depends(get_current_org),
):
    try:
        point_ids = ingest_pipeline.ingest_text(document, org_id=org_id)
        return {"ingested": len(point_ids), "point_ids": point_ids}
    except Exception as e:
        logger.error("Ingest failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seed", response_model=dict)
async def seed_knowledge(
    user: User = Depends(require_permission("knowledge:create")),
    org_id: str = Depends(get_current_org),
):
    try:
        ingest_pipeline.seed_default_knowledge(org_id=org_id)
        return {"status": "ok", "message": "Default knowledge seeded"}
    except Exception as e:
        logger.error("Seed failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{collection_name}/{point_id}")
async def delete_document(
    collection_name: str,
    point_id: str,
    user: User = Depends(require_permission("knowledge:delete")),
    org_id: str = Depends(get_current_org),
):
    try:
        qdrant_service.delete_document(collection_name, point_id, org_id=org_id)
        return {"deleted": True}
    except Exception as e:
        logger.error("Delete failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
