import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.billing.schemas import PLANS, CheckoutRequest, CheckoutResponse, BillingPortalRequest
from app.billing.service import stripe_service
from app.billing.limits import get_org_plan_state
from app.infrastructure.usage.meter import usage_meter, METERED_FIELDS
from app.middleware.tenant_context import TenantContext, get_tenant_context

logger = logging.getLogger("proposalcraft.billing.router")

router = APIRouter()


@router.get("/plans")
async def list_plans():
    return {"plans": PLANS}


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: CheckoutRequest,
    ctx: TenantContext = Depends(get_tenant_context("billing:update")),
):
    try:
        return await stripe_service.create_checkout_session(
            plan_id=body.plan_id,
            interval=body.interval,
            org_id=ctx.organization_id,
            return_url=body.return_url,
        )
    except Exception as e:
        logger.error("Checkout failed: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscription")
async def get_subscription(
    ctx: TenantContext = Depends(get_tenant_context("billing:update")),
):
    sub = await stripe_service.get_subscription(ctx.organization_id)
    if not sub:
        return {"plan_id": "free", "status": "active", "plan": next((p for p in PLANS if p["id"] == "free"), None)}
    return sub


@router.post("/cancel")
async def cancel_subscription(
    ctx: TenantContext = Depends(get_tenant_context("billing:update")),
):
    cancelled = await stripe_service.cancel_subscription(ctx.organization_id)
    return {"cancelled": cancelled}


@router.post("/portal")
async def billing_portal(
    body: BillingPortalRequest,
    ctx: TenantContext = Depends(get_tenant_context("billing:update")),
):
    try:
        url = await stripe_service.create_billing_portal(ctx.organization_id, body.return_url)
        return {"url": url}
    except Exception as e:
        logger.error("Portal failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/usage")
async def get_usage(
    ctx: TenantContext = Depends(get_tenant_context("billing:read")),
):
    state = await get_org_plan_state(ctx.organization_id)
    usage = await usage_meter.get_org_usage(ctx.organization_id)
    return {
        "plan_id": state["plan_id"],
        "period": usage.get("period"),
        "usage": {k: usage.get(k, 0) for k in METERED_FIELDS},
        "limits": state["limits"],
        "proposals_remaining": state["proposals_remaining"],
    }


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    try:
        await stripe_service.handle_webhook(payload, sig_header)
        return {"received": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
