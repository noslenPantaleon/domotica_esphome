from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ClienteBase(BaseModel):
    nombre:   str
    email:    Optional[EmailStr] = None
    telefono: Optional[str]      = None
    activo:   bool               = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nombre:   Optional[str]      = None
    email:    Optional[EmailStr] = None
    telefono: Optional[str]      = None
    activo:   Optional[bool]     = None


class ClienteResponse(ClienteBase):
    cliente_id:     int
    fecha_registro: datetime

    model_config = {"from_attributes": True}
