from motor.motor_asyncio import AsyncIOMotorClient

from src.config.settings import settings

client = AsyncIOMotorClient(settings.mongodb_url)
database = client.mastergrow


async def get_mongo_db():
    return database