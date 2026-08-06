import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from app.billing.schemas import PLANS, CheckoutRequest, CheckoutResponse, BillingPortalRequest
from app.billing.service import stripe_service
from app.config.constants import OrganizationPlan, PLAN_LIMITS
from app.domain.entities.user import User
from app.api.deps import get_current_user, get_current_org
from app.infrastructure.usage.meter import usage_meter, METERED_FIELDS

logger = logging.getLogger("proposalcraft.billing.router")

router = APIRouter()


@router.get("/plans")
async def list_plans():
    return {"plans": PLANS}


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: CheckoutRequest,
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org),
):
    try:
        return await stripe_service.create_checkout_session(
            plan_id=body.plan_id,
            interval=body.interval,
            org_id=org_id,
            return_url=body.return_url,
        )
    except Exception as e:
        logger.error("Checkout failed: %s", e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscription")
async def get_subscription(
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org),
):
    sub = await stripe_service.get_subscription(org_id)
    if not sub:
        return {"plan_id": "free", "status": "active", "plan": next((p for p in PLANS if p["id"] == "free"), None)}
    return sub


@router.post("/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org),
):
    cancelled = await stripe_service.cancel_subscription(org_id)
    return {"cancelled": cancelled}


@router.post("/portal")
async def billing_portal(
    body: BillingPortalRequest,
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org),
):
    try:
        url = await stripe_service.create_billing_portal(org_id, body.return_url)
        return {"url": url}
    except Exception as e:
        logger.error("Portal failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/usage")
async def get_usage(
    user: User = Depends(get_current_user),
    org_id: str = Depends(get_current_org),
):
    sub = await stripe_service.get_subscription(org_id)
    plan_id = sub.plan_id if sub else "free"
    limits = PLAN_LIMITS.get(OrganizationPlan(plan_id), PLAN_LIMITS[OrganizationPlan.FREE])
    usage = await usage_meter.get_org_usage(org_id)
    used = usage.get("proposals_generated", 0)
    return {
        "plan_id": plan_id,
        "period": usage.get("period"),
        "usage": {k: usage.get(k, 0) for k in METERED_FIELDS},
        "limits": limits,
        "proposals_remaining": max(0, limits["proposals_per_month"] - used),
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
