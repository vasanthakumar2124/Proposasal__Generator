from datetime import datetime, timezone
from typing import Awaitable, Callable

from app.config.settings import settings
from app.domain.events import DomainEvent
from app.infrastructure.database.mongodb import get_database
from app.infrastructure.log.logger import logger

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []
        self._enabled = settings.ENABLE_ACTIVITY_EVENTS

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    async def publish(self, event: DomainEvent) -> None:
        if not self._enabled:
            return
        await self._persist(event)
        for handler in self._handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error("Event handler %s failed for %s: %s", handler.__name__, event.event_type, e)

    async def _persist(self, event: DomainEvent) -> None:
        try:
            db = await get_database()
            await db.activity_events.insert_one(
                {
                    "event_type": event.event_type,
                    "organization_id": event.organization_id,
                    "user_id": event.user_id,
                    "resource_type": event.resource_type,
                    "resource_id": event.resource_id,
                    "payload": event.payload,
                    "occurred_at": event.occurred_at,
                }
            )
        except Exception as e:
            logger.error("Failed to persist activity event %s: %s", event.event_type, e)


event_bus = EventBus()
