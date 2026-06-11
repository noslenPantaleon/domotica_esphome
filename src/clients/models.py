from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class Client(Base):
    __tablename__ = "clients"

    client_id         = Column(Integer, primary_key=True, autoincrement=True)
    name              = Column(String(100), nullable=False)
    email             = Column(String(100), unique=True, nullable=True)
    phone             = Column(String(20), nullable=True)
    registration_date = Column(DateTime, server_default=func.now(), nullable=False)
    active            = Column(Boolean, default=True, nullable=False)

    users           = relationship("User",        back_populates="client", cascade="all, delete")
    invoices        = relationship("Invoice",     back_populates="client", cascade="all, delete")
    client_devices  = relationship("ClientDevice", back_populates="client", cascade="all, delete")
