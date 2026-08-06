from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.organizations import router as orgs_router
from app.api.v1.workspaces import router as workspaces_router
from app.api.v1.members import router as members_router
from app.api.v1.clients import router as clients_router
from app.api.v1.projects import router as projects_router
from app.api.v1.proposals import router as proposals_router
from app.rag.router import router as rag_router
from app.export.router import router as export_router
from app.billing.router import router as billing_router
from app.analytics.router import router as analytics_router
from app.admin.router import router as admin_router
from app.api.v1.activity import router as activity_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(orgs_router, prefix="/orgs", tags=["Organizations"])
api_router.include_router(workspaces_router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(members_router, prefix="/members", tags=["Members"])
api_router.include_router(clients_router, prefix="/clients", tags=["Clients"])
api_router.include_router(projects_router, prefix="/projects", tags=["Projects"])
api_router.include_router(proposals_router, prefix="/proposals", tags=["Proposals"])
api_router.include_router(rag_router, prefix="/rag", tags=["RAG"])
api_router.include_router(export_router, tags=["Export"])
api_router.include_router(billing_router, prefix="/billing", tags=["Billing"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(activity_router, prefix="/activity", tags=["Activity"])
