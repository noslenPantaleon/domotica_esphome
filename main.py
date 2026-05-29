from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Domótica API",
    description="API for IoT domotics system — ESPHome + MQTT + aioesphomeapi",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all models with SQLAlchemy so relationship strings resolve at startup
from src.clientes.models import Cliente              # noqa: F401
from src.ubicaciones.models import Ubicacion         # noqa: F401
from src.usuarios.models import Usuario              # noqa: F401
from src.facturacion.models import Facturacion       # noqa: F401
from src.dispositivos.models import ClienteDispositivo  # noqa: F401

# Schema is managed by Alembic — run: alembic upgrade head

# MQTT
try:
    from src.mqtt.handler import mqtt_handler
    mqtt_handler.start()
    print("MQTT handler started")

    @app.on_event("shutdown")
    def shutdown_event():
        mqtt_handler.stop()
        print("MQTT handler stopped")
except Exception as e:
    print(f"MQTT init failed: {e}")

# Routers
from src.auth.router import router as auth_router
from src.usuarios.router import router as usuarios_router
from src.clientes.router import router as clientes_router
from src.facturacion.router import router as facturacion_router
from src.ubicaciones.router import router as ubicaciones_router
from src.dispositivos.router import router as dispositivos_router
from src.mqtt.router import router as mqtt_router

app.include_router(auth_router,        prefix="/auth",        tags=["auth"])
app.include_router(usuarios_router,    prefix="/usuarios",    tags=["usuarios"])
app.include_router(clientes_router,    prefix="/clientes",    tags=["clientes"])
app.include_router(facturacion_router, prefix="/facturacion", tags=["facturacion"])
app.include_router(ubicaciones_router, prefix="/ubicaciones", tags=["ubicaciones"])
app.include_router(dispositivos_router,prefix="/dispositivos",tags=["dispositivos"])
app.include_router(mqtt_router,        prefix="/mqtt",        tags=["mqtt"])


@app.get("/", tags=["root"], include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["root"])
async def health():
    return {"status": "healthy"}
