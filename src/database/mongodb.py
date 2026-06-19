# from motor.motor_asyncio import AsyncIOMotorClient

# from src.config.settings import settings

# client = AsyncIOMotorClient(settings.mongodb_url)

# # Extract database name from the URL (last path segment)
# _db_name = settings.mongodb_url.rstrip("/").rsplit("/", 1)[-1]
# database = client[_db_name]


# async def get_mongo_db():
#     return database

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from dotenv import load_dotenv

# Configuración de logs para ver en consola qué hace la base de datos
logger = logging.getLogger("uvicorn.error")

load_dotenv()

# 1. Recuperamos la URI y la base de datos validada
MONGO_URI = os.getenv(
    "MONGO_URI", 
    "mongodb+srv://scaautomatizaciones_db_user2:Daniel24204359@cluster0.ld4nidu.mongodb.net/?appName=Cluster0"
)
# 🛠️ CORRECCIÓN: Cambiado de "domotica" a "domotic" para que coincida exactamente con Atlas
DB_NAME = os.getenv("MONGO_DB_NAME", "domotic")

# 2. Inicializamos el cliente global
client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)
database: AsyncIOMotorDatabase = client[DB_NAME]

async def check_mongo_connection():
    """Valida la conexión real con Atlas lanzando un comando ping."""
    try:
        await client.admin.command('ping', timeoutMS=5000)
        logger.info(f"✅ Conexión exitosa a MongoDB Atlas establecida en la base de datos '{DB_NAME}'.")
    except Exception as e:
        logger.error(f"❌ Error crítico al conectar a MongoDB Atlas: {e}")

async def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Dependencia para inyectar la base de datos en los routers de FastAPI.
    Uso: mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
    """
    return database
