import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from app.config.settings import settings
from app.infrastructure.database.mongodb import get_database
from app.infrastructure.log.logger import logger
from app.infrastructure.usage.context import get_usage_context

METERED_FIELDS = (
    "proposals_generated",
    "llm_calls",
    "input_tokens",
    "output_tokens",
    "cost",
)

_main_loop: Optional[asyncio.AbstractEventLoop] = None


def set_usage_loop(loop: asyncio.AbstractEventLoop) -> None:
    global _main_loop
    if _main_loop is None:
        _main_loop = loop


def current_period() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


class UsageMeter:
    async def record_proposal_generation(self, org_id: str, user_id: str, proposal_id: str) -> None:
        await self._increment(org_id, user_id, {"proposals_generated": 1})

    async def record_llm_call(
        self,
        org_id: str,
        user_id: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ) -> None:
        await self._increment(
            org_id,
            user_id,
            {
                "llm_calls": 1,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": round(cost, 6),
            },
        )

    async def _increment(self, org_id: str, user_id: str, inc: dict) -> None:
        if not settings.ENABLE_USAGE_METERING or not org_id:
            return
        try:
            db = await get_database()
            period = current_period()
            await db.usage.update_one(
                {"organization_id": org_id, "period": period},
                {
                    "$inc": inc,
                    "$setOnInsert": {
                        "organization_id": org_id,
                        "user_id": user_id,
                        "period": period,
                        "created_at": datetime.now(timezone.utc),
                    },
                },
                upsert=True,
            )
        except Exception as e:
            logger.error("Failed to record usage for org %s: %s", org_id, e)

    async def get_org_usage(self, org_id: str, period: Optional[str] = None) -> dict:
        try:
            db = await get_database()
            doc = await db.usage.find_one(
                {"organization_id": org_id, "period": period or current_period()}
            )
        except Exception as e:
            logger.error("Failed to read usage for org %s: %s", org_id, e)
            doc = None
        if not doc:
            return {"period": period or current_period(), **{k: 0 for k in METERED_FIELDS}}
        return {k: doc.get(k, 0) for k in METERED_FIELDS} | {"period": doc.get("period")}


usage_meter = UsageMeter()


def record_llm_call_sync(provider: str, model: str, input_tokens: int, output_tokens: int, cost: float) -> None:
    org_id, user_id = get_usage_context()
    if not settings.ENABLE_USAGE_METERING or not org_id:
        return
    if _main_loop is not None and _main_loop.is_running():
        asyncio.run_coroutine_threadsafe(
            usage_meter.record_llm_call(org_id, user_id, provider, model, input_tokens, output_tokens, cost),
            _main_loop,
        )
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.debug("No event loop available, skipping usage record")
        return
    loop.create_task(
        usage_meter.record_llm_call(org_id, user_id, provider, model, input_tokens, output_tokens, cost)
    )
