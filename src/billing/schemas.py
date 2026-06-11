from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

from src.billing.models import InvoiceStatusEnum


class InvoiceBase(BaseModel):
    client_id:      int
    issue_date:     date
    due_date:       date
    amount:         Decimal
    status:         InvoiceStatusEnum = InvoiceStatusEnum.pending
    payment_method: Optional[str]     = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceUpdate(BaseModel):
    due_date:       Optional[date]            = None
    amount:         Optional[Decimal]         = None
    status:         Optional[InvoiceStatusEnum] = None
    payment_method: Optional[str]             = None


class InvoiceResponse(InvoiceBase):
    invoice_id: int

    model_config = {"from_attributes": True}
