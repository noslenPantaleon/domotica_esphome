from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class UbicacionBase(BaseModel):
    pais:         str
    comuna:       Optional[str]     = None
    calle:        Optional[str]     = None
    numero_calle: Optional[int]     = None
    latitud:      Optional[Decimal] = None
    longitud:     Optional[Decimal] = None


class UbicacionCreate(UbicacionBase):
    pass


class UbicacionUpdate(BaseModel):
    pais:         Optional[str]     = None
    comuna:       Optional[str]     = None
    calle:        Optional[str]     = None
    numero_calle: Optional[int]     = None
    latitud:      Optional[Decimal] = None
    longitud:     Optional[Decimal] = None


class UbicacionResponse(UbicacionBase):
    ubicacion_id: int

    model_config = {"from_attributes": True}
