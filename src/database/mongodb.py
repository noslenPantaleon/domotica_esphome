import logging
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase

# Importamos la configuración centralizada
from src.config.settings import settings

logger = logging.getLogger("uvicorn.error")

# 1. Inicializamos el cliente global usando el objeto settings blindado
client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_URI)
database: AsyncIOMotorDatabase = client[settings.MONGO_DB_NAME]

async def check_mongo_connection():
    """Valida la conexión real con Atlas lanzando un comando ping."""
    try:
        await client.admin.command('ping', timeoutMS=5000)
        logger.info(f"✅ Conexión exitosa a MongoDB Atlas establecida en la base de datos '{settings.MONGO_DB_NAME}'.")
    except Exception as e:
        logger.error(f"❌ Error crítico al conectar a MongoDB Atlas: {e}")

async def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Dependencia para inyectar la base de datos en los routers de FastAPI.
    Uso: mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
    """
    return database