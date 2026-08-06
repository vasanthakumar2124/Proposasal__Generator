from fastapi import HTTPException

from app.billing.service import stripe_service
from app.config.constants import OrganizationPlan, PLAN_LIMITS
from app.config.settings import settings
from app.infrastructure.usage.meter import usage_meter


async def get_org_plan_state(org_id: str) -> dict:
    sub = await stripe_service.get_subscription(org_id)
    plan_id = sub.plan_id if sub else "free"
    limits = PLAN_LIMITS.get(OrganizationPlan(plan_id), PLAN_LIMITS[OrganizationPlan.FREE])
    usage = await usage_meter.get_org_usage(org_id)
    used = usage.get("proposals_generated", 0)
    return {
        "plan_id": plan_id,
        "limits": limits,
        "proposals_used": used,
        "proposals_remaining": max(0, limits["proposals_per_month"] - used),
    }


async def enforce_proposal_limit(org_id: str) -> None:
    if not settings.ENABLE_USAGE_METERING:
        return
    state = await get_org_plan_state(org_id)
    if state["proposals_remaining"] <= 0:
        raise HTTPException(
            status_code=402,
            detail=(
                f"Monthly proposal limit reached ({state['proposals_used']}/{state['limits']['proposals_per_month']}). "
                "Upgrade your plan to continue generating proposals."
            ),
        )
