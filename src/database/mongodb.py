from motor.motor_asyncio import AsyncIOMotorClient

from src.config.settings import settings

client = AsyncIOMotorClient(settings.mongodb_url)

# Extract database name from the URL (last path segment)
_db_name = settings.mongodb_url.rstrip("/").rsplit("/", 1)[-1]
database = client[_db_name]


async def get_mongo_db():
    return database
