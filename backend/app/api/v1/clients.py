from fastapi import APIRouter, Depends, HTTPException

from app.domain.entities.user import User
from app.schemas.client import ClientCreateRequest, ClientUpdateRequest, ClientResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.client_service import ClientService
from app.api.deps import get_current_user, get_current_org, require_permission

router = APIRouter()


@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(
    body: ClientCreateRequest,
    user: User = Depends(require_permission("client:create")),
    org_id: str = Depends(get_current_org),
):
    svc = ClientService()
    client = await svc.create_client(body.model_dump(exclude_unset=True), org_id, user.id)
    return ClientResponse(**client.model_dump(by_alias=True))


@router.get("", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    skip: int = 0, limit: int = 100,
    user: User = Depends(require_permission("client:read")),
    org_id: str = Depends(get_current_org),
):
    svc = ClientService()
    clients = await svc.list_clients(org_id, skip=skip, limit=limit)
    items = [ClientResponse(**c.model_dump(by_alias=True)) for c in clients]
    return PaginatedResponse(items=items, total=len(items), skip=skip, limit=limit)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    user: User = Depends(require_permission("client:read")),
):
    svc = ClientService()
    try:
        client = await svc.get_client(client_id)
        if client.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return ClientResponse(**client.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str, body: ClientUpdateRequest,
    user: User = Depends(require_permission("client:update")),
):
    svc = ClientService()
    try:
        client = await svc.update_client(client_id, body.model_dump(exclude_unset=True))
        if client.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return ClientResponse(**client.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{client_id}", response_model=MessageResponse)
async def delete_client(
    client_id: str,
    user: User = Depends(require_permission("client:delete")),
):
    svc = ClientService()
    try:
        client = await svc.get_client(client_id)
        if client.organization_id != user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
        await svc.delete_client(client_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MessageResponse(message="Client deleted")
