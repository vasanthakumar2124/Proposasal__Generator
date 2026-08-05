import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config.settings import settings
from app.infrastructure.cache.rate_limit_store import rate_limit_store

logger = logging.getLogger("proposalcraft.middleware.rate_limit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._window = settings.RATE_LIMIT_WINDOW_SECONDS
        self._per_user = settings.RATE_LIMIT_PER_USER
        self._per_org = settings.RATE_LIMIT_PER_ORG

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        now = time.time()

        user_id = request.headers.get("X-User-Id", request.client.host if request.client else "unknown")
        org_id = request.headers.get("X-Org-Id", "unknown")

        user_key = f"user:{user_id}"
        org_key = f"org:{org_id}"

        user_count = rate_limit_store.add(user_key, now, self._window)
        org_count = rate_limit_store.add(org_key, now, self._window)

        if user_count > self._per_user:
            logger.warning("Rate limit exceeded for user %s: %d", user_id, user_count)
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})

        if org_count > self._per_org and org_id != "unknown":
            logger.warning("Rate limit exceeded for org %s: %d", org_id, org_count)
            return JSONResponse(status_code=429, content={"detail": "Organization rate limit exceeded."})

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self._per_user - user_count))
        return response
