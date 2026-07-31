import time
import logging
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config.settings import settings

logger = logging.getLogger("proposalcraft.middleware.rate_limit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._window = settings.RATE_LIMIT_WINDOW_SECONDS
        self._per_user = settings.RATE_LIMIT_PER_USER
        self._per_org = settings.RATE_LIMIT_PER_ORG

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        now = time.time()
        cutoff = now - self._window

        user_id = request.headers.get("X-User-Id", request.client.host if request.client else "unknown")
        org_id = request.headers.get("X-Org-Id", "unknown")

        user_key = f"user:{user_id}"
        org_key = f"org:{org_id}"

        self._clean(cutoff, user_key)
        self._clean(cutoff, org_key)

        user_count = len(self._requests[user_key])
        org_count = len(self._requests[org_key])

        if user_count >= self._per_user:
            logger.warning("Rate limit exceeded for user %s: %d", user_id, user_count)
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})

        if org_count >= self._per_org and org_id != "unknown":
            logger.warning("Rate limit exceeded for org %s: %d", org_id, org_count)
            return JSONResponse(status_code=429, content={"detail": "Organization rate limit exceeded."})

        self._requests[user_key].append(now)
        self._requests[org_key].append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self._per_user - len(self._requests[user_key])))
        return response

    def _clean(self, cutoff: float, key: str) -> None:
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]
