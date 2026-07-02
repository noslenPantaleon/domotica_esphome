from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal
from src.billing.models import InvoiceStatus

class InvoiceBase(BaseModel):
    client_id: int
    amount: Decimal
    status: InvoiceStatus = InvoiceStatus.pending
    due_date: datetime

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceUpdate(BaseModel):
    amount: Optional[Decimal] = None
    status: Optional[InvoiceStatus] = None
    due_date: Optional[datetime] = None

class InvoiceResponse(InvoiceBase):
    invoice_id: int
    created_at: datetime

    model_config = {"from_attributes": True}