import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.domain.entities.user import User
from app.domain.events import EVENT_PROPOSAL_FAILED
from app.domain.exceptions import TokenExpiredError, TokenInvalidError
from app.infrastructure.auth.jwt import verify_access_token
from app.infrastructure.events.streams import ProposalEventTailer
from app.services.auth_service import AuthService
from app.services.generated_proposal_service import GeneratedProposalService
from app.infrastructure.di.container import get_service

logger = logging.getLogger("proposalcraft.realtime_router")

router = APIRouter()

HEARTBEAT_SECONDS = 15
MAX_STREAM_SECONDS = 40 * 60


async def get_sse_user(
    request: Request,
    auth_service: AuthService = Depends(get_service(AuthService)),
) -> User:
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header[7:]
    if not token:
        token = request.query_params.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = verify_access_token(token)
    except TokenExpiredError:
        raise HTTPException(status_code=401, detail="Token expired")
    except TokenInvalidError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await auth_service.get_current_user(payload.get("sub"))
    if not user or user.status != "active":
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


@router.get("/proposals/{proposal_id}/events")
async def stream_proposal_events(
    proposal_id: str,
    user: User = Depends(get_sse_user),
    svc: GeneratedProposalService = Depends(get_service(GeneratedProposalService)),
):
    if not user.has_permission("proposal:read"):
        raise HTTPException(status_code=403, detail="Missing permission: proposal:read")

    try:
        doc = await svc.get_proposal(proposal_id)
    except Exception:
        doc = None
    if not doc or str(doc.get("organization_id")) != user.organization_id:
        raise HTTPException(status_code=404, detail="Proposal not found")

    initial = {
        "proposal_id": proposal_id,
        "status": doc.get("status", "draft"),
        "title": doc.get("title"),
        "error": doc.get("error"),
    }

    async def event_source() -> AsyncGenerator[str, None]:
        yield f"event: connected\ndata: {json.dumps(initial)}\n\n"

        tailer = ProposalEventTailer(proposal_id, user.organization_id)
        event_iter = tailer.events()
        next_task = asyncio.create_task(anext(event_iter))
        loop = asyncio.get_running_loop()
        deadline = loop.time() + MAX_STREAM_SECONDS
        try:
            while True:
                done, _ = await asyncio.wait({next_task}, timeout=HEARTBEAT_SECONDS)
                if not done:
                    if loop.time() >= deadline:
                        break
                    yield ": ping\n\n"
                    continue
                try:
                    event = next_task.result()
                except StopAsyncIteration:
                    break
                status = "failed" if event["event_type"] == EVENT_PROPOSAL_FAILED else "draft"
                data = {
                    "proposal_id": proposal_id,
                    "status": status,
                    "event_type": event["event_type"],
                    "title": event["payload"].get("title"),
                    "error": event["payload"].get("error"),
                    "occurred_at": event["occurred_at"].isoformat() if event["occurred_at"] else None,
                }
                yield f"event: status\ndata: {json.dumps(data)}\n\n"
                next_task = asyncio.create_task(anext(event_iter))
        finally:
            next_task.cancel()
            try:
                await event_iter.aclose()
            except Exception:
                pass

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
