import enum
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class InvoiceStatusEnum(str, enum.Enum):
    pending  = "pending"
    paid     = "paid"
    overdue  = "overdue"


class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id     = Column(Integer, primary_key=True, autoincrement=True)
    client_id      = Column(Integer, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
    issue_date     = Column(Date, nullable=False)
    due_date       = Column(Date, nullable=False)
    amount         = Column(Numeric(10, 2), nullable=False)
    status         = Column(Enum(InvoiceStatusEnum), default=InvoiceStatusEnum.pending, nullable=False)
    payment_method = Column(String(50), nullable=True)

    # Relación opcional para acceder al cliente desde la factura
    client = relationship("Client", back_populates="invoices")
