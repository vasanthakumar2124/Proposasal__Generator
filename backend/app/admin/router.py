import logging

from fastapi import APIRouter, Depends, HTTPException

from app.database.mongodb import db
from app.domain.entities.user import User
from app.api.deps import get_current_user, require_permission

logger = logging.getLogger("proposalcraft.admin.router")

router = APIRouter()


@router.get("/health")
async def system_health():
    try:
        await db.command("ping")
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
    }


@router.get("/users")
async def list_users(
    user: User = Depends(require_permission("admin")),
):
    cursor = db.users.find({}).sort("created_at", -1).limit(100)
    users = []
    async for u in cursor:
        u["_id"] = str(u["_id"])
        u.pop("hashed_password", None)
        users.append(u)
    return {"users": users}


@router.get("/organizations")
async def list_organizations(
    user: User = Depends(require_permission("admin")),
):
    cursor = db.organizations.find({}).sort("created_at", -1).limit(100)
    orgs = []
    async for o in cursor:
        o["_id"] = str(o["_id"])
        orgs.append(o)
    return {"organizations": orgs}
