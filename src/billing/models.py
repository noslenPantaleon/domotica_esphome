from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from src.database.mysql import Base

class InvoiceStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"

class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id  = Column(Integer, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
    amount     = Column(Numeric(10, 2), nullable=False)
    status     = Column(Enum(InvoiceStatus), default=InvoiceStatus.pending, nullable=False)
    due_date   = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relación bidireccional con Client
    client = relationship("Client", back_populates="invoices")
