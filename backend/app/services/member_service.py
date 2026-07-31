from typing import Optional

from app.config.constants import UserRole, DEFAULT_PERMISSIONS
from app.domain.entities.user import User
from app.domain.exceptions import EntityNotFoundError, DuplicateEntityError
from app.domain.interfaces import UserRepository, OrganizationRepository
from app.infrastructure.database.mongo_repositories.user_repo import MongoUserRepository
from app.infrastructure.database.mongo_repositories.org_repo import MongoOrganizationRepository
from app.infrastructure.log.audit import create_audit_log
from app.infrastructure.auth.password import hash_password


class MemberService:
    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        org_repo: Optional[OrganizationRepository] = None,
    ) -> None:
        self.user_repo = user_repo or MongoUserRepository()
        self.org_repo = org_repo or MongoOrganizationRepository()

    async def add_member(self, org_id: str, email: str, role: str, invited_by: str) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise DuplicateEntityError("User", "email", email)

        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise EntityNotFoundError("Organization", org_id)

        user_role = UserRole(role) if role in [r.value for r in UserRole] else UserRole.EDITOR
        temp_password = f"temp_{org_id[-6:]}"

        user = User(
            email=email,
            password_hash=hash_password(temp_password),
            name=email.split("@")[0],
            organization_id=org_id,
            role=user_role,
            permissions=DEFAULT_PERMISSIONS[user_role],
            status="active",
        )
        user = await self.user_repo.create(user)

        await create_audit_log(
            organization_id=org_id,
            user_id=invited_by,
            action="member.invite",
            resource_type="user",
            resource_id=user.id,
        )

        return user

    async def update_member_role(self, org_id: str, user_id: str, new_role: str, updated_by: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.organization_id != org_id:
            raise EntityNotFoundError("User", user_id)

        user_role = UserRole(new_role)
        user.role = user_role
        user.permissions = DEFAULT_PERMISSIONS[user_role]
        user = await self.user_repo.update(user)

        await create_audit_log(
            organization_id=org_id,
            user_id=updated_by,
            action="member.role_update",
            resource_type="user",
            resource_id=user_id,
        )

        return user

    async def remove_member(self, org_id: str, user_id: str, removed_by: str) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.organization_id != org_id:
            raise EntityNotFoundError("User", user_id)

        user.status = "deactivated"
        await self.user_repo.update(user)

        await create_audit_log(
            organization_id=org_id,
            user_id=removed_by,
            action="member.remove",
            resource_type="user",
            resource_id=user_id,
        )

    async def list_members(self, org_id: str, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.user_repo.get_by_organization(org_id, skip=skip, limit=limit)
