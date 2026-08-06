from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_current_org, require_permission
from app.domain.entities.user import User
from app.infrastructure.database.mongodb import get_database
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[dict])
async def list_activity(
    skip: int = 0,
    limit: int = Query(50, ge=1, le=200),
    event_type: str = Query(None),
    user: User = Depends(require_permission("activity:read")),
    org_id: str = Depends(get_current_org),
):
    db = await get_database()
    query: dict = {"organization_id": org_id}
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
