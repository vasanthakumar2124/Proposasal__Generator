from fastapi import APIRouter, Depends, HTTPException

from app.schemas.client import ClientCreateRequest, ClientUpdateRequest, ClientResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.client_service import ClientService
from app.infrastructure.di.container import get_service
from app.middleware.tenant_context import TenantContext, get_tenant_context, ensure_tenant_access

router = APIRouter()


@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(
    body: ClientCreateRequest,
    ctx: TenantContext = Depends(get_tenant_context("client:create")),
    svc: ClientService = Depends(get_service(ClientService)),
):
    client = await svc.create_client(body.model_dump(exclude_unset=True), ctx.organization_id, ctx.user.id)
    return ClientResponse(**client.model_dump(by_alias=True))


@router.get("", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    skip: int = 0, limit: int = 100,
    ctx: TenantContext = Depends(get_tenant_context("client:read")),
    svc: ClientService = Depends(get_service(ClientService)),
):
    clients = await svc.list_clients(ctx.organization_id, skip=skip, limit=limit)
    items = [ClientResponse(**c.model_dump(by_alias=True)) for c in clients]
    return PaginatedResponse(items=items, total=len(items), skip=skip, limit=limit)


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    ctx: TenantContext = Depends(get_tenant_context("client:read")),
    svc: ClientService = Depends(get_service(ClientService)),
):
    try:
        client = await svc.get_client(client_id)
        ensure_tenant_access(client, ctx)
        return ClientResponse(**client.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str, body: ClientUpdateRequest,
    ctx: TenantContext = Depends(get_tenant_context("client:update")),
    svc: ClientService = Depends(get_service(ClientService)),
):
    try:
        client = await svc.update_client(client_id, body.model_dump(exclude_unset=True))
        ensure_tenant_access(client, ctx)
        return ClientResponse(**client.model_dump(by_alias=True))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{client_id}", response_model=MessageResponse)
async def delete_client(
    client_id: str,
    ctx: TenantContext = Depends(get_tenant_context("client:delete")),
    svc: ClientService = Depends(get_service(ClientService)),
):
    try:
        client = await svc.get_client(client_id)
        ensure_tenant_access(client, ctx)
        await svc.delete_client(client_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MessageResponse(message="Client deleted")
