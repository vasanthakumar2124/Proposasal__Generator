import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.export.service import export_service
from app.export.normalize import normalize_proposal

logger = logging.getLogger("proposalcraft.export.router")

router = APIRouter(prefix="/export", tags=["Export"])


@router.post("/{fmt}")
async def export_proposal(
    fmt: str,
    proposal: dict,
    filename: Optional[str] = Query(None),
):
    if fmt not in ("html", "pdf", "docx", "pptx"):
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")
    try:
        proposal = normalize_proposal(proposal)
        path = export_service.export(proposal, fmt, filename)
        media_types = {
            "html": "text/html",
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        }
        return FileResponse(
            path=path,
            media_type=media_types.get(fmt, "application/octet-stream"),
            filename=Path(path).name,
        )
    except Exception as e:
        logger.error("Export failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/all")
async def export_all(proposal: dict):
    try:
        results = export_service.export_all(proposal)
        return {"exported": results}
    except Exception as e:
        logger.error("Batch export failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
