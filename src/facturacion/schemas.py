from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

from src.facturacion.models import EstadoFacturaEnum


class FacturacionBase(BaseModel):
    cliente_id:        int
    fecha_emision:     date
    fecha_vencimiento: date
    monto:             Decimal
    estado:            EstadoFacturaEnum = EstadoFacturaEnum.pendiente
    metodo_pago:       Optional[str]     = None


class FacturacionCreate(FacturacionBase):
    pass


class FacturacionUpdate(BaseModel):
    fecha_vencimiento: Optional[date]             = None
    monto:             Optional[Decimal]           = None
    estado:            Optional[EstadoFacturaEnum] = None
    metodo_pago:       Optional[str]               = None


class FacturacionResponse(FacturacionBase):
    factura_id: int

    model_config = {"from_attributes": True}
