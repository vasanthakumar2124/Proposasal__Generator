from typing import Optional

from app.domain.entities.user import User
from app.domain.exceptions import EntityNotFoundError
from app.domain.interfaces import UserRepository
from app.infrastructure.database.mongo_repositories.user_repo import MongoUserRepository
from app.infrastructure.log.audit import create_audit_log


class UserService:
    def __init__(self, user_repo: Optional[UserRepository] = None) -> None:
        self.user_repo = user_repo or MongoUserRepository()

    async def get_user(self, user_id: str) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        return user

    async def update_user(self, user_id: str, name: Optional[str] = None, avatar_url: Optional[str] = None) -> User:
        user = await self.get_user(user_id)
        if name is not None:
            user.name = name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        user = await self.user_repo.update(user)

        await create_audit_log(
            organization_id=user.organization_id,
            user_id=user_id,
            action="user.update",
            resource_type="user",
            resource_id=user_id,
        )

        return user

    async def list_organization_members(self, org_id: str, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.user_repo.get_by_organization(org_id, skip=skip, limit=limit)
