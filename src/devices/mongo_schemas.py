from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ── Embedded: sensor configuration ──────────────────────────────────────────

class SensorConfig(BaseModel):
    alarm_threshold: Optional[float] = None
    notifications:   bool            = True


# ── Embedded: individual sensor inside a device ─────────────────────────────

class EmbeddedSensor(BaseModel):
    sensor_name:   str
    sensor_type:   str
    unit:          str
    last_reading:  Optional[datetime]    = None
    last_value:    Optional[float]       = None
    last_quality:  Optional[str]         = None
    config:        Optional[SensorConfig] = None


# ── Embedded: device state history entry ────────────────────────────────────

class StateHistoryEntry(BaseModel):
    date:  datetime
    state: str
    notes: Optional[str] = None


# ── Main device document ─────────────────────────────────────────────────────

class DeviceMongoBase(BaseModel):
    device_name:       str
    device_type:       str
    location:          str
    client_id:         int
    overall_state:     str                     = "active"
    installation_date: Optional[datetime]      = None
    sensors:           List[EmbeddedSensor]     = []
    state_history:     List[StateHistoryEntry]  = []


class DeviceMongoCreate(DeviceMongoBase):
    id: str = Field(alias="_id")  # e.g. "ESP32_001"

    model_config = {"populate_by_name": True}


class DeviceMongoResponse(DeviceMongoBase):
    id: str = Field(alias="_id")

    model_config = {"populate_by_name": True}


# ── Sensor reading (for MQTT ingestion) ─────────────────────────────────────

class SensorReading(BaseModel):
    device_id:   str
    sensor_name: str
    sensor_type: str
    value:       float
    unit:        str
    timestamp:   datetime = Field(default_factory=datetime.utcnow)
