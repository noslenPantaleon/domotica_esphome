from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Domotica API",
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
from src.clients.models import Client          # noqa: F401
from src.locations.models import Location      # noqa: F401
from src.users.models import User              # noqa: F401
from src.billing.models import Invoice         # noqa: F401
from src.devices.models import ClientDevice    # noqa: F401

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
from src.users.router import router as users_router
from src.clients.router import router as clients_router
from src.billing.router import router as billing_router
from src.locations.router import router as locations_router
from src.devices.router import router as devices_router
from src.mqtt.router import router as mqtt_router

app.include_router(auth_router,      prefix="/auth",      tags=["auth"])
app.include_router(users_router,     prefix="/users",     tags=["users"])
app.include_router(clients_router,   prefix="/clients",   tags=["clients"])
app.include_router(billing_router,   prefix="/billing",   tags=["billing"])
app.include_router(locations_router, prefix="/locations", tags=["locations"])
app.include_router(devices_router,   prefix="/devices",   tags=["devices"])
app.include_router(mqtt_router,      prefix="/mqtt",      tags=["mqtt"])


@app.get("/", tags=["root"], include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health", tags=["root"])
async def health():
    return {"status": "healthy"}
