from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


PLANS = [
    {"id": "free", "name": "Free", "price_monthly": 0, "price_yearly": 0, "proposals": 3, "exports": "html"},
    {"id": "starter", "name": "Starter", "price_monthly": 29, "price_yearly": 290, "proposals": 20, "exports": "html,pdf"},
    {"id": "professional", "name": "Professional", "price_monthly": 79, "price_yearly": 790, "proposals": 100, "exports": "all", "features": ["priority_support"]},
    {"id": "enterprise", "name": "Enterprise", "price_monthly": 199, "price_yearly": 1990, "proposals": -1, "exports": "all", "features": ["priority_support", "api_access", "custom_branding", "dedicated_support"]},
]


class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price_monthly: int
    price_yearly: int
    proposals: int
    exports: str
    features: list[str] = []


class SubscriptionResponse(BaseModel):
    id: str
    organization_id: str
    plan_id: str
    status: Literal["active", "past_due", "canceled", "trialing", "incomplete"]
    current_period_start: datetime
    current_period_end: datetime
    stripe_subscription_id: str
    cancel_at_period_end: bool = False
    plan: Optional[SubscriptionPlan] = None


class CheckoutRequest(BaseModel):
    plan_id: str = Field(..., pattern="^(free|starter|professional|enterprise)$")
    interval: Literal["month", "year"] = "month"
    return_url: str = "http://localhost:5173/dashboard"


class CheckoutResponse(BaseModel):
    url: str
    session_id: str


class BillingPortalRequest(BaseModel):
    return_url: str = "http://localhost:5173/billing"
