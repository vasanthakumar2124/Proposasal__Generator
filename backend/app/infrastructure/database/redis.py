import redis.asyncio as redis
from typing import Optional
from app.config.settings import settings

redis_client: Optional[redis.Redis] = None


async def connect_to_redis() -> None:
    global redis_client
    if not settings.REDIS_URL:
        return
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        max_connections=20,
    )
    await redis_client.ping()


async def close_redis_connection() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_redis() -> Optional[redis.Redis]:
    return redis_client
