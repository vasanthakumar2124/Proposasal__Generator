from fastapi import APIRouter, Depends, HTTPException, Request

from app.domain.entities.user import User
from app.domain.exceptions import DuplicateEntityError, InvalidCredentialsError
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshTokenRequest,
    AuthResponse, TokenResponse, UserResponse, UserUpdateRequest,
)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: RegisterRequest):
    auth_service = AuthService()
    try:
        user, org, access_token, refresh_token = await auth_service.register(
            name=body.name,
            email=body.email,
            password=body.password,
            company_name=body.company_name,
        )
    except DuplicateEntityError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            _id=user.id,
            email=user.email,
            name=user.name,
            organization_id=user.organization_id,
            role=user.role.value,
            avatar_url=user.avatar_url,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest):
    auth_service = AuthService()
    try:
        user, org, access_token, refresh_token = await auth_service.login(
            email=body.email,
            password=body.password,
        )
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=str(e))

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            _id=user.id,
            email=user.email,
            name=user.name,
            organization_id=user.organization_id,
            role=user.role.value,
            avatar_url=user.avatar_url,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshTokenRequest):
    auth_service = AuthService()
    try:
        access_token, refresh_token = await auth_service.refresh_token(body.refresh_token)
    except (InvalidCredentialsError) as e:
        raise HTTPException(status_code=401, detail=str(e))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=900,
    )


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


@router.put("/me", response_model=UserResponse)
async def update_me(body: UserUpdateRequest, user: User = Depends(get_current_user)):
    user_service = UserService()
    updated = await user_service.update_user(
        user_id=user.id,
        name=body.name,
        avatar_url=body.avatar_url,
    )
    return UserResponse(
        _id=updated.id,
        email=updated.email,
        name=updated.name,
        organization_id=updated.organization_id,
        role=updated.role.value,
        avatar_url=updated.avatar_url,
        status=updated.status,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(user: User = Depends(get_current_user)):
    return MessageResponse(message="Logged out successfully")
