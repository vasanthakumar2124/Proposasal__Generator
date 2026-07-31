from typing import Optional

from app.domain.entities.organization import Organization
from app.domain.exceptions import EntityNotFoundError
from app.domain.interfaces import OrganizationRepository
from app.infrastructure.database.mongo_repositories.org_repo import MongoOrganizationRepository
from app.infrastructure.log.audit import create_audit_log


class OrganizationService:
    def __init__(self, org_repo: Optional[OrganizationRepository] = None) -> None:
        self.org_repo = org_repo or MongoOrganizationRepository()

    async def get_organization(self, org_id: str) -> Organization:
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise EntityNotFoundError("Organization", org_id)
        return org

    async def update_organization(
        self, org_id: str, name: Optional[str] = None,
        branding: Optional[dict] = None, settings: Optional[dict] = None,
    ) -> Organization:
        org = await self.get_organization(org_id)
        if name is not None:
            org.name = name
        if branding is not None:
            org.branding = type(org.branding)(**branding) if isinstance(branding, dict) else branding
        if settings is not None:
            org.settings.update(settings)
        org = await self.org_repo.update(org)

        await create_audit_log(
            organization_id=org_id,
            user_id="system",
            action="organization.update",
            resource_type="organization",
            resource_id=org_id,
        )

        return org
