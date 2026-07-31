from datetime import datetime, timezone
from typing import Optional

from app.config.settings import settings
from app.infrastructure.database.mongodb import get_database
from app.infrastructure.log.logger import logger


async def create_audit_log(
    organization_id: str,
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    if not settings.ENABLE_AUDIT_LOG:
        return

    try:
        db = await get_database()
        await db.audit_logs.insert_one({
            "organization_id": organization_id,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": ip_address or "",
            "user_agent": user_agent or "",
            "created_at": datetime.now(timezone.utc),
        })
    except Exception as e:
        logger.error("Failed to create audit log: %s", e)
