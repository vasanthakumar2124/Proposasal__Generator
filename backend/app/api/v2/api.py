from fastapi import APIRouter

from app.api.v2.projects import router as projects_router

api_v2_router = APIRouter(prefix="/api/v2")

api_v2_router.include_router(projects_router, prefix="/projects", tags=["Projects Hub (v2)"])
