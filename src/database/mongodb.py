import logging
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase

# Importamos la configuración centralizada
from src.config.settings import settings

logger = logging.getLogger("uvicorn.error")

# 1. Inicializamos el cliente global usando el objeto settings blindado
client: AsyncIOMotorClient = AsyncIOMotorClient(settings.mongodb_url)
database: AsyncIOMotorDatabase = client[settings.mongo_db_name]

async def check_mongo_connection():
    try:
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB database '{settings.mongo_db_name}'.")
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")

async def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Dependencia para inyectar la base de datos en los routers de FastAPI.
    Uso: mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
    """
    return database