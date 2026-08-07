from typing import Callable, Type

from app.services.auth_service import AuthService
from app.services.client_service import ClientService
from app.services.generated_proposal_service import GeneratedProposalService
from app.services.member_service import MemberService
from app.services.organization_service import OrganizationService
from app.services.project_service import ProjectService
from app.services.proposal_service import ProposalService
from app.services.proposal_version_service import ProposalVersionService
from app.services.user_service import UserService
from app.services.workspace_service import WorkspaceService

ServiceType = (
    AuthService
    | ClientService
    | GeneratedProposalService
    | MemberService
    | OrganizationService
    | ProjectService
    | ProposalService
    | ProposalVersionService
    | UserService
    | WorkspaceService
)

ServiceFactory = Callable[[], ServiceType]


class Container:
    """Central service registry. Every service is constructed here and
    resolved through the get_service() FastAPI dependency, so routers never
    construct services inline."""

    def __init__(self) -> None:
        self._factories: dict[Type, ServiceFactory] = {}

    def register(self, service_type: Type, factory: ServiceFactory) -> None:
        self._factories[service_type] = factory

    def get(self, service_type: Type) -> ServiceType:
        factory = self._factories.get(service_type)
        if factory is None:
            raise KeyError(f"No factory registered for {service_type.__name__}")
        return factory()


container = Container()

container.register(AuthService, lambda: AuthService())
container.register(ClientService, lambda: ClientService())
container.register(GeneratedProposalService, lambda: GeneratedProposalService())
container.register(MemberService, lambda: MemberService())
container.register(OrganizationService, lambda: OrganizationService())
container.register(ProjectService, lambda: ProjectService())
container.register(ProposalService, lambda: ProposalService())
container.register(ProposalVersionService, lambda: ProposalVersionService())
container.register(UserService, lambda: UserService())
container.register(WorkspaceService, lambda: WorkspaceService())


def get_service(service_type: Type) -> ServiceFactory:
    return lambda: container.get(service_type)
