import logging
from datetime import datetime, timezone
from typing import Optional

import stripe
from bson import ObjectId

from app.config.settings import settings
from app.billing.schemas import PLANS, SubscriptionPlan, CheckoutResponse, SubscriptionResponse
from app.models.subscription_model import subscription_collection

logger = logging.getLogger("proposalcraft.billing")

stripe.api_key = settings.STRIPE_SECRET_KEY

STRIPE_PRICE_MAP: dict[str, dict[str, str]] = {
    "free": {"month": "", "year": ""},
    "starter": {"month": "price_starter_monthly", "year": "price_starter_yearly"},
    "professional": {"month": "price_professional_monthly", "year": "price_professional_yearly"},
    "enterprise": {"month": "price_enterprise_monthly", "year": "price_enterprise_yearly"},
}


class StripeService:
    async def create_checkout_session(self, plan_id: str, interval: str, org_id: str, return_url: str) -> CheckoutResponse:
        if plan_id == "free":
            await self._activate_free_plan(org_id)
            return CheckoutResponse(url=return_url, session_id="free")

        price_id = STRIPE_PRICE_MAP.get(plan_id, {}).get(interval)
        if not price_id:
            price_id = await self._lookup_or_create_price(plan_id, interval)

        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={"org_id": org_id, "plan_id": plan_id},
            success_url=return_url + "?billing=success",
            cancel_url=return_url + "?billing=canceled",
            client_reference_id=org_id,
        )
        return CheckoutResponse(url=session.url, session_id=session.id)

    async def handle_webhook(self, payload: bytes, sig_header: str) -> None:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            logger.error("Webhook verification failed: %s", e)
            raise

        handler = {
            "checkout.session.completed": self._handle_checkout_completed,
            "invoice.paid": self._handle_invoice_paid,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
        }.get(event.type)

        if handler:
            await handler(event.data.object)
        else:
            logger.debug("Unhandled webhook event: %s", event.type)

    async def get_subscription(self, org_id: str) -> Optional[SubscriptionResponse]:
        sub = await subscription_collection.find_one(
            {"organization_id": org_id, "status": {"$in": ["active", "past_due", "trialing"]}},
            sort=[("current_period_end", -1)],
        )
        if not sub:
            return None
        plan = next((p for p in PLANS if p["id"] == sub.get("plan_id")), None)
        return SubscriptionResponse(
            id=str(sub["_id"]),
            organization_id=sub["organization_id"],
            plan_id=sub["plan_id"],
            status=sub["status"],
            current_period_start=sub["current_period_start"],
            current_period_end=sub["current_period_end"],
            stripe_subscription_id=sub.get("stripe_subscription_id", ""),
            cancel_at_period_end=sub.get("cancel_at_period_end", False),
            plan=SubscriptionPlan(**plan) if plan else None,
        )

    async def cancel_subscription(self, org_id: str) -> bool:
        sub = await subscription_collection.find_one({"organization_id": org_id, "status": "active"})
        if not sub or not sub.get("stripe_subscription_id"):
            return False
        try:
            stripe.Subscription.modify(sub["stripe_subscription_id"], cancel_at_period_end=True)
            await subscription_collection.update_one(
                {"_id": sub["_id"]}, {"$set": {"cancel_at_period_end": True}}
            )
            return True
        except stripe.error.StripeError as e:
            logger.error("Cancel failed: %s", e)
            return False

    async def create_billing_portal(self, org_id: str, return_url: str) -> str:
        sub = await subscription_collection.find_one({"organization_id": org_id})
        if not sub or not sub.get("stripe_customer_id"):
            session = stripe.billing_portal.Session.create(
                customer=sub["stripe_customer_id"],
                return_url=return_url,
            )
            return session.url
        return return_url

    async def _activate_free_plan(self, org_id: str) -> None:
        now = datetime.now(timezone.utc)
        await subscription_collection.update_one(
            {"organization_id": org_id, "plan_id": "free"},
            {"$set": {
                "plan_id": "free", "status": "active",
                "current_period_start": now, "current_period_end": now,
                "stripe_subscription_id": "", "stripe_customer_id": "",
            }},
            upsert=True,
        )

    async def _handle_checkout_completed(self, session: stripe.checkout.Session) -> None:
        org_id = session.metadata.get("org_id")
        plan_id = session.metadata.get("plan_id")
        sub_id = session.get("subscription")
        customer_id = session.get("customer")
        if not org_id:
            return
        if sub_id:
            sub = stripe.Subscription.retrieve(sub_id)
            now = datetime.now(timezone.utc)
            await subscription_collection.update_one(
                {"organization_id": org_id},
                {"$set": {
                    "plan_id": plan_id,
                    "status": sub.status,
                    "current_period_start": datetime.fromtimestamp(sub.current_period_start, tz=timezone.utc),
                    "current_period_end": datetime.fromtimestamp(sub.current_period_end, tz=timezone.utc),
                    "stripe_subscription_id": sub_id,
                    "stripe_customer_id": customer_id,
                }},
                upsert=True,
            )
            logger.info("Subscription activated for org %s: %s", org_id, plan_id)

    async def _handle_invoice_paid(self, invoice: stripe.Invoice) -> None:
        sub_id = invoice.get("subscription")
        if sub_id:
            try:
                sub = stripe.Subscription.retrieve(sub_id)
                org_id = sub.metadata.get("org_id")
                if org_id:
                    await subscription_collection.update_one(
                        {"organization_id": org_id},
                        {"$set": {
                            "status": sub.status,
                            "current_period_start": datetime.fromtimestamp(sub.current_period_start, tz=timezone.utc),
                            "current_period_end": datetime.fromtimestamp(sub.current_period_end, tz=timezone.utc),
                        }},
                    )
            except stripe.error.StripeError:
                pass

    async def _handle_subscription_updated(self, sub: stripe.Subscription) -> None:
        org_id = sub.metadata.get("org_id")
        if org_id:
            await subscription_collection.update_one(
                {"organization_id": org_id},
                {"$set": {
                    "status": sub.status,
                    "cancel_at_period_end": sub.cancel_at_period_end,
                    "current_period_end": datetime.fromtimestamp(sub.current_period_end, tz=timezone.utc),
                }},
            )

    async def _handle_subscription_deleted(self, sub: stripe.Subscription) -> None:
        org_id = sub.metadata.get("org_id")
        if org_id:
            await subscription_collection.update_one(
                {"organization_id": org_id},
                {"$set": {"status": "canceled"}},
            )

    async def _lookup_or_create_price(self, plan_id: str, interval: str) -> str:
        plan = next((p for p in PLANS if p["id"] == plan_id), None)
        if not plan:
            raise ValueError(f"Unknown plan: {plan_id}")
        amount = plan["price_yearly"] if interval == "year" else plan["price_monthly"]
        product = stripe.Product.create(name=plan["name"], metadata={"plan_id": plan_id})
        price = stripe.Price.create(
            product=product.id,
            unit_amount=amount * 100,
            currency="usd",
            recurring={"interval": interval},
        )
        return price.id


stripe_service = StripeService()
