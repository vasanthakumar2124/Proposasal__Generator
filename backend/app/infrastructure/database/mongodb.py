from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect_to_mongodb() -> None:
    global client, db
    client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
        minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
    )
    db = client[settings.DATABASE_NAME]
    await client.admin.command("ping")


async def close_mongodb_connection() -> None:
    global client
    if client:
        client.close()
        client = None


async def get_database() -> AsyncIOMotorDatabase:
    if db is None:
        await connect_to_mongodb()
    return db


async def ensure_indexes() -> None:
    database = await get_database()

    await database.users.create_index("email", unique=True)
    await database.users.create_index("organization_id")
    await database.users.create_index([("email", 1), ("organization_id", 1)])

    await database.organizations.create_index("slug", unique=True)

    await database.proposals.create_index("organization_id")
    await database.proposals.create_index([("organization_id", 1), ("status", 1)])
    await database.proposals.create_index([("organization_id", 1), ("created_at", -1)])

    await database.generated_proposals.create_index("organization_id")
    await database.generated_proposals.create_index([("user_id", 1), ("created_at", -1)])

    await database.clients.create_index("organization_id")
    await database.clients.create_index([("organization_id", 1), ("name", 1)])

    await database.projects.create_index("organization_id")
    await database.projects.create_index([("organization_id", 1), ("status", 1)])

    await database.workspaces.create_index("organization_id")

    await database.audit_logs.create_index("organization_id")
    await database.audit_logs.create_index([("organization_id", 1), ("created_at", -1)])

    await database.activity_events.create_index("organization_id")
    await database.activity_events.create_index([("organization_id", 1), ("occurred_at", -1)])
    await database.activity_events.create_index([("organization_id", 1), ("event_type", 1), ("occurred_at", -1)])
    await database.activity_events.create_index([("organization_id", 1), ("resource_id", 1), ("occurred_at", 1)])

    await database.usage.create_index("organization_id")
    await database.usage.create_index([("organization_id", 1), ("created_at", -1)])
    await database.usage.create_index([("organization_id", 1), ("period", 1)], unique=True)
