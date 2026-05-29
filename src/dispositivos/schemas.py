from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ClienteDispositivoBase(BaseModel):
    cliente_id:           int
    ubicacion_id:         int
    dispositivo_mongo_id: str


class ClienteDispositivoCreate(ClienteDispositivoBase):
    pass


class ClienteDispositivoUpdate(BaseModel):
    ubicacion_id:         Optional[int] = None
    dispositivo_mongo_id: Optional[str] = None


class ClienteDispositivoResponse(ClienteDispositivoBase):
    id:               int
    fecha_asociacion: datetime

    model_config = {"from_attributes": True}
