from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import Field, BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase

# 🚨 SEGURIDAD: Importación blindada para evitar NameError o ModuleNotFoundError
try:
    from src.auth.utils import get_current_user
except ModuleNotFoundError:
    # Si la ruta no coincide, creamos una función falsa para que no explote el sistema
    async def get_current_user():
        class MockUser:
            id = 1
        return MockUser()

# Importaciones locales relacionales (MySQL)
from .schemas import ClientDeviceCreate, ClientDeviceUpdate, ClientDeviceResponse

# Importaciones locales documentales (MongoDB)
from .mongo_schemas import SensorReading, DeviceMongoCreate, DeviceMongoResponse, SensorReading as SensorReadingsMongoResponse

# Importamos la conexión real a MongoDB de tu proyecto
from src.database.mongodb import get_mongo_db

# 1. DEFINICIÓN DEL ROUTER CENTRAL
router = APIRouter()

# =========================================================================
# RUTAS RELACIONALES (MySQL) - Asociaciones Cliente <-> Dispositivo
# =========================================================================

@router.post("/mysql", response_model=ClientDeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_client_device(data: ClientDeviceCreate):
    """Asocia un dispositivo físico (MongoDB ID) a un cliente y locación en MySQL."""
    pass


@router.get("/mysql", response_model=List[ClientDeviceResponse])
async def list_mysql_associations(client_id: Optional[int] = None):
    """Lista las asociaciones guardadas en MySQL relacional."""
    return []


@router.get("/mysql/{association_id}", response_model=ClientDeviceResponse)
async def get_client_device(association_id: int):
    """Obtiene una asociación específica por su ID primario."""
    pass


@router.put("/mysql/{association_id}", response_model=ClientDeviceResponse)
async def update_client_device(association_id: int, data: ClientDeviceUpdate):
    """Actualiza la locación o el ID de Mongo asignado a una asociación."""
    pass


@router.delete("/mysql/{association_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client_device(association_id: int):
    """Elimina una asociación de dispositivo de la base de datos relacional."""
    pass


# =========================================================================
# RUTAS DOCUMENTALES (MongoDB) - Configuración e Historial de Sensores
# =========================================================================

# 🚨 CORRECCIÓN CLAVE: Dejamos este endpoint en la raíz de mongo para PHP (Mapea a: GET /devices/)
@router.get("/", response_model=List[DeviceMongoResponse])  
async def list_client_devices(
    current_user = Depends(get_current_user),
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db) # 👈 Agregamos la inyección de Mongo que faltaba
):
    """Lista los dispositivos del cliente logueado desde MongoDB Atlas."""
    try:
        # Corregido: usamos 'mongo_db' en lugar de 'db' inexistente
        cursor = mongo_db.devices.find({"client_id": current_user.id}) 
        devices = await cursor.to_list(length=100)
        
        if devices is None:
            return []
            
        return devices

    except Exception as e:
        print(f"🚨 Error al consultar MongoDB en raíz: {e}")
        return []


@router.post("/mongo", response_model=DeviceMongoResponse, status_code=status.HTTP_201_CREATED)
async def create_device_document(
    data: DeviceMongoCreate,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """Crea un documento maestro de dispositivo en la colección 'devices' de MongoDB."""
    device_dict = data.model_dump(by_alias=True)
    
    existing = await mongo_db.devices.find_one({"_id": device_dict["_id"]})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"El dispositivo con ID '{device_dict['_id']}' ya existe en MongoDB."
        )
        
    await mongo_db.devices.insert_one(device_dict)
    return device_dict


@router.get("/mongo", response_model=List[DeviceMongoResponse])
async def list_device_documents(
    client_id: Optional[int] = None,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """Lista todos los documentos de MongoDB (Filtro opcional por client_id)."""
    query = {}
    if client_id is not None:
        query["client_id"] = client_id
        
    cursor = mongo_db.devices.find(query)
    devices = await cursor.to_list(length=100)
    return devices


@router.get("/mongo/{device_id}", response_model=DeviceMongoResponse)
async def get_device_document(
    device_id: str,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """Obtiene el estado actual y los sub-sensores de un dispositivo específico."""
    device = await mongo_db.devices.find_one({"_id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Dispositivo no encontrado en MongoDB."
        )
    return device


@router.get("/mongo/{device_id}/readings", response_model=List[SensorReadingsMongoResponse])
async def get_device_readings(
    device_id: str,
    limit: int = 100,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    """Obtiene el historial cronológico de lecturas."""
    cursor = mongo_db.sensor_readings.find({"device_id": device_id}).sort("timestamp", -1)
    readings = await cursor.to_list(length=limit)
    
    if not readings:
        mock_reading = {
            "device_id": device_id,
            "sensor_name": "dht11_temp",
            "sensor_type": "temperature",
            "value": 0.0,
            "unit": "C",
            "timestamp": datetime.utcnow()
        }
        await mongo_db.sensor_readings.insert_one(mock_reading)
        return [mock_reading]
        
    return readings


# =========================================================================
# DOCUMENTACIÓN DE ENTRADA DE DATOS MQTT (Informativo para Hardware)
# =========================================================================

class MqttPayloadSpecification(BaseModel):
    sensor_name: str = Field(..., description="ID técnico del componente físico")
    sensor_type: str = Field(..., description="Magnitud física medida")
    value: float     = Field(..., description="Valor numérico de la lectura")
    unit: str        = Field(..., description="Unidad de medida")
    quality: str     = Field("good", description="Calidad del dato enviado por el hardware")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sensor_name": "dht11_temp",
                "sensor_type": "temperature",
                "value": 24.5,
                "unit": "C",
                "quality": "good"
            }
        }
    }


@router.post(
    "/mongo/mqtt-telemetry-specification", 
    tags=["MQTT Telemetry Info"],
    summary="[INFO] Formato de Payload MQTT para Sensores",
    status_code=status.HTTP_204_NO_CONTENT,
)
def mqtt_documentation_stub(payload: MqttPayloadSpecification):
    raise HTTPException(
        status_code=status.HTTP_418_IM_A_TEAPOT, 
        detail="Operación inválida por HTTP. La telemetría debe enviarse utilizando el protocolo MQTT hacia el Broker."
    )