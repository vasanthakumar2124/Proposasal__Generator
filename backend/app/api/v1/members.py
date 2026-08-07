from fastapi import APIRouter, Depends, HTTPException

from app.domain.entities.user import User
from app.domain.exceptions import DuplicateEntityError
from app.schemas.auth import UserResponse
from app.schemas.organization import AddMemberRequest, MemberResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.member_service import MemberService
from app.api.deps import get_current_user, get_current_org, require_permission
from app.infrastructure.di.container import get_service

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=201)
async def invite_member(
    body: AddMemberRequest,
    user: User = Depends(require_permission("member:create")),
    org_id: str = Depends(get_current_org),
    svc: MemberService = Depends(get_service(MemberService)),
):
    try:
        member = await svc.add_member(
            org_id=org_id,
            email=body.email,
            role=body.role,
            invited_by=user.id,
        )
    except DuplicateEntityError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return UserResponse(
        _id=member.id, email=member.email, name=member.name,
        organization_id=member.organization_id, role=member.role.value,
        avatar_url=member.avatar_url, status=member.status,
        created_at=member.created_at, updated_at=member.updated_at,
    )


@router.get("", response_model=PaginatedResponse[MemberResponse])
async def list_members(
    skip: int = 0,
    limit: int = 100,
    user: User = Depends(require_permission("member:read")),
    org_id: str = Depends(get_current_org),
    svc: MemberService = Depends(get_service(MemberService)),
):
    members = await svc.list_members(org_id, skip=skip, limit=limit)
    items = [
        MemberResponse(
            id=m.id, name=m.name, email=m.email,
            role=m.role.value, status=m.status,
            last_login=m.last_login,
        )
        for m in members
    ]
    return PaginatedResponse(items=items, total=len(items), skip=skip, limit=limit)


@router.put("/{user_id}/role", response_model=MemberResponse)
async def update_member_role(
    user_id: str,
    body: dict,
    user: User = Depends(require_permission("member:update")),
    org_id: str = Depends(get_current_org),
    svc: MemberService = Depends(get_service(MemberService)),
):
    role = body.get("role")
    if not role:
        raise HTTPException(status_code=400, detail="Role is required")

    try:
        member = await svc.update_member_role(
            org_id=org_id,
            user_id=user_id,
            new_role=role,
            updated_by=user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    return MemberResponse(
        id=member.id, name=member.name, email=member.email,
        role=member.role.value, status=member.status,
        last_login=member.last_login,
    )


@router.delete("/{user_id}", response_model=MessageResponse)
async def remove_member(
    user_id: str,
    user: User = Depends(require_permission("member:delete")),
    org_id: str = Depends(get_current_org),
    svc: MemberService = Depends(get_service(MemberService)),
):
    try:
        await svc.remove_member(
            org_id=org_id,
            user_id=user_id,
            removed_by=user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    return MessageResponse(message="Member removed")
