from fastapi import APIRouter

from app.api.v2.projects import router as projects_router
from app.api.v2.proposals import router as proposals_router

api_v2_router = APIRouter(prefix="/api/v2")

api_v2_router.include_router(projects_router, prefix="/projects", tags=["Projects Hub (v2)"])
api_v2_router.include_router(proposals_router, prefix="/proposals", tags=["Proposal Lifecycle (v2)"])
