from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ── Embedded: sensor configuration ──────────────────────────────────────────

class SensorConfiguracion(BaseModel):
    umbral_alarma:  Optional[float] = None
    notificaciones: bool            = True


# ── Embedded: individual sensor inside a device ─────────────────────────────

class SensorEmbebido(BaseModel):
    nombre_sensor:  str
    tipo_sensor:    str
    unidad_medida:  str
    ultima_lectura: Optional[datetime]          = None
    valor_ultimo:   Optional[float]             = None
    calidad_ultimo: Optional[str]               = None
    configuracion:  Optional[SensorConfiguracion] = None


# ── Embedded: device state history entry ────────────────────────────────────

class HistoricoEstado(BaseModel):
    fecha:         datetime
    estado:        str
    observaciones: Optional[str] = None


# ── Main device document ─────────────────────────────────────────────────────

class DispositivoMongoBase(BaseModel):
    nombre_dispositivo: str
    tipo_dispositivo:   str
    ubicacion:          str
    cliente_id:         int
    estado_general:     str                    = "activo"
    fecha_instalacion:  Optional[datetime]     = None
    sensores:           List[SensorEmbebido]   = []
    historico_estados:  List[HistoricoEstado]  = []


class DispositivoMongoCreate(DispositivoMongoBase):
    id: str = Field(alias="_id")  # e.g. "ESP32_001"

    model_config = {"populate_by_name": True}


class DispositivoMongoResponse(DispositivoMongoBase):
    id: str = Field(alias="_id")

    model_config = {"populate_by_name": True}


# ── Sensor reading (for MQTT ingestion) ─────────────────────────────────────

class LecturaSensor(BaseModel):
    dispositivo_id: str
    nombre_sensor:  str
    tipo_sensor:    str
    valor:          float
    unidad_medida:  str
    timestamp:      datetime = Field(default_factory=datetime.utcnow)
