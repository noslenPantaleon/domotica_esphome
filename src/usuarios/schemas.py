from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from src.usuarios.models import RolEnum


class UsuarioBase(BaseModel):
    nombre:     str
    email:      EmailStr
    rol:        RolEnum
    cliente_id: int


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioUpdate(BaseModel):
    nombre:   Optional[str]      = None
    email:    Optional[EmailStr] = None
    rol:      Optional[RolEnum]  = None
    password: Optional[str]      = None


class UsuarioResponse(UsuarioBase):
    usuario_id:     int
    fecha_creacion: datetime
    ultimo_login:   Optional[datetime] = None

    model_config = {"from_attributes": True}
