from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ESPHomeConnectRequest(BaseModel):
    host:     str
    port:     int  = 6053
    password: str  = ""


class ESPHomeSwitchCommand(BaseModel):
    state: bool


class ESPHomeLightCommand(BaseModel):
    state:       bool
    brightness:  Optional[float] = Field(None, ge=0.0, le=1.0)
    red:         Optional[float] = Field(None, ge=0.0, le=1.0)
    green:       Optional[float] = Field(None, ge=0.0, le=1.0)
    blue:        Optional[float] = Field(None, ge=0.0, le=1.0)
    color_temp:  Optional[float] = None


class ESPHomeEntityInfo(BaseModel):
    key:       int
    name:      str
    object_id: str
    entity_type: str


class ESPHomeStateRecord(BaseModel):
    device_id:   str
    key:         int
    entity_name: str
    entity_type: str
    state:       Any
    unit:        Optional[str] = None
    timestamp:   datetime = Field(default_factory=datetime.utcnow)


class ESPHomeConnectionStatus(BaseModel):
    device_id: str
    host:      str
    port:      int
    connected: bool
