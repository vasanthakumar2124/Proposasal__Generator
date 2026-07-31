from datetime import datetime, timezone
from typing import Optional

from app.config.constants import UserRole, DEFAULT_PERMISSIONS
from app.domain.entities.user import User
from app.domain.entities.organization import Organization
from app.domain.exceptions import (
    DuplicateEntityError,
    InvalidCredentialsError,
    TokenInvalidError,
    TokenExpiredError,
)
from app.domain.interfaces import UserRepository, OrganizationRepository
from app.infrastructure.auth.jwt import create_access_token, create_refresh_token, verify_access_token
from app.infrastructure.auth.password import hash_password, verify_password
from app.infrastructure.log.audit import create_audit_log
from app.infrastructure.database.mongo_repositories.user_repo import MongoUserRepository
from app.infrastructure.database.mongo_repositories.org_repo import MongoOrganizationRepository


class AuthService:
    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        org_repo: Optional[OrganizationRepository] = None,
    ) -> None:
        self.user_repo = user_repo or MongoUserRepository()
        self.org_repo = org_repo or MongoOrganizationRepository()

    async def register(
        self, name: str, email: str, password: str, company_name: str
    ) -> tuple[User, Organization, str, str]:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise DuplicateEntityError("User", "email", email)

        slug = company_name.lower().replace(" ", "-").replace("_", "-")[:50]
        org = Organization(name=company_name, slug=slug)
        org = await self.org_repo.create(org)

        password_hash = hash_password(password)
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            organization_id=org.id,
            role=UserRole.ADMIN,
            permissions=DEFAULT_PERMISSIONS[UserRole.ADMIN],
        )
        user = await self.user_repo.create(user)

        access_token = create_access_token(user.id, {"org_id": org.id, "role": user.role.value})
        refresh_token = create_refresh_token(user.id)

        await create_audit_log(
            organization_id=org.id,
            user_id=user.id,
            action="auth.register",
            resource_type="user",
            resource_id=user.id,
        )

        return user, org, access_token, refresh_token

    async def login(self, email: str, password: str) -> tuple[User, Organization, str, str]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        if user.status != "active":
            raise InvalidCredentialsError("Account is inactive")

        org = await self.org_repo.get_by_id(user.organization_id)
        if not org or org.status != "active":
            raise InvalidCredentialsError("Organization is inactive")

        user.update_login()
        await self.user_repo.update(user)

        access_token = create_access_token(user.id, {"org_id": org.id, "role": user.role.value, "permissions": user.permissions})
        refresh_token = create_refresh_token(user.id)

        await create_audit_log(
            organization_id=org.id,
            user_id=user.id,
            action="auth.login",
            resource_type="user",
            resource_id=user.id,
        )

        return user, org, access_token, refresh_token

    async def refresh_token(self, refresh_token: str) -> tuple[str, str]:
        try:
            payload = verify_access_token(refresh_token)
        except TokenExpiredError:
            raise TokenExpiredError("Refresh token expired")
        except TokenInvalidError:
            raise TokenInvalidError("Invalid refresh token")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user or user.status != "active":
            raise InvalidCredentialsError("User not found or inactive")

        org = await self.org_repo.get_by_id(user.organization_id)
        if not org or org.status != "active":
            raise InvalidCredentialsError("Organization inactive")

        new_access = create_access_token(user.id, {"org_id": org.id, "role": user.role.value, "permissions": user.permissions})
        new_refresh = create_refresh_token(user.id)

        return new_access, new_refresh

    async def get_current_user(self, user_id: str) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)
