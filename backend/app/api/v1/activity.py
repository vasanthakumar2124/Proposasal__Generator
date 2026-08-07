from fastapi import APIRouter, Depends, Query

from app.infrastructure.database.mongodb import get_database
from app.schemas.common import PaginatedResponse
from app.middleware.tenant_context import TenantContext, get_tenant_context

router = APIRouter()


@router.get("", response_model=PaginatedResponse[dict])
async def list_activity(
    skip: int = 0,
    limit: int = Query(50, ge=1, le=200),
    event_type: str = Query(None),
    ctx: TenantContext = Depends(get_tenant_context("activity:read")),
):
    db = await get_database()
    query: dict = {"organization_id": ctx.organization_id}
    if event_type:
        query["event_type"] = event_type
    cursor = (
        db.activity_events.find(query)
        .sort("occurred_at", -1)
        .skip(skip)
        .limit(limit)
    )
    items = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["occurred_at"] = doc["occurred_at"].isoformat()
        items.append(doc)
    return PaginatedResponse(items=items, total=len(items), skip=skip, limit=limit)
