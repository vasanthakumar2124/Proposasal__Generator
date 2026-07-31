from fastapi import Request
from app.infrastructure.database.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_db(request: Request) -> AsyncIOMotorDatabase:
    return await get_database()
