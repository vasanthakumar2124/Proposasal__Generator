import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException

from app.config.settings import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def _upload_dir() -> Path:
    base = Path(settings.UPLOAD_DIR if settings.UPLOAD_DIR else "uploads")
    return base


def _validate(upload: UploadFile) -> str:
    filename = upload.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext or 'none'}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )
    if upload.size is not None and upload.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )
    return ext


class UploadService:
    async def save(self, upload: UploadFile, org_id: str) -> tuple[Path, str]:
        ext = _validate(upload)
        org_dir = _upload_dir() / org_id
        org_dir.mkdir(parents=True, exist_ok=True)
        dest = org_dir / f"{uuid.uuid4().hex}{ext}"

        size = 0
        with dest.open("wb") as out:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
                    out.close()
                    dest.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB} MB",
                    )
                out.write(chunk)
        return dest, ext


upload_service = UploadService()
