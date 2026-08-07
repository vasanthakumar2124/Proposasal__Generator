from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.domain.entities.user import User
from app.domain.exceptions import TokenExpiredError, TokenInvalidError
from app.infrastructure.auth.jwt import verify_access_token
from app.services.auth_service import AuthService
from app.config.constants import DEFAULT_PERMISSIONS
from app.infrastructure.di.container import get_service

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_service(AuthService)),
) -> User:

    if credentials:
        token = credentials.credentials
    elif x_api_key:
        token = x_api_key
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = verify_access_token(token)
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="Token expired")
    except TokenInvalidError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    user = await auth_service.get_current_user(user_id)
    if not user or user.status != "active":
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


async def get_current_org(user: User = Depends(get_current_user)) -> str:
    return user.organization_id


def require_permission(permission: str):
    async def permission_checker(user: User = Depends(get_current_user)) -> User:
        if not user.has_permission(permission):
            raise HTTPException(status_code=403, detail=f"Missing permission: {permission}")
        return user
    return permission_checker


async def get_pagination(
    skip: int = 0,
    limit: int = 100,
) -> tuple[int, int]:
    return skip, min(limit, 500)
