from app.domain.interfaces.user_repo import UserRepository
from app.domain.interfaces.org_repo import OrganizationRepository
from app.domain.interfaces.workspace_repo import WorkspaceRepository
from app.domain.interfaces.client_repo import ClientRepository
from app.domain.interfaces.project_repo import ProjectRepository
from app.domain.interfaces.proposal_repo import ProposalRepository

__all__ = [
    "UserRepository",
    "OrganizationRepository",
    "WorkspaceRepository",
    "ClientRepository",
    "ProjectRepository",
    "ProposalRepository",
]
