from fastapi import APIRouter, Depends

from app.domain.entities.user import User
from app.schemas.auth import UserResponse
from app.schemas.organization import MemberResponse
from app.schemas.common import PaginatedResponse
from app.services.user_service import UserService
from app.api.deps import get_current_user, get_current_org, require_permission
from app.infrastructure.di.container import get_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        _id=user.id,
        email=user.email,
        name=user.name,
        organization_id=user.organization_id,
        role=user.role.value,
        avatar_url=user.avatar_url,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.get("/members", response_model=PaginatedResponse[MemberResponse])
async def list_members(
    skip: int = 0,
    limit: int = 100,
    org_id: str = Depends(get_current_org),
    user: User = Depends(require_permission("member:read")),
    user_service: UserService = Depends(get_service(UserService)),
):
    members = await user_service.list_organization_members(org_id, skip=skip, limit=limit)
    items = [
        MemberResponse(
            id=m.id,
            name=m.name,
            email=m.email,
            role=m.role.value,
            status=m.status,
            last_login=m.last_login,
        )
        for m in members
    ]
    return PaginatedResponse(items=items, total=len(items), skip=skip, limit=limit)
