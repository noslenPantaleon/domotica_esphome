from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class Cliente(Base):
    __tablename__ = "clientes"

    cliente_id     = Column(Integer, primary_key=True, autoincrement=True)
    nombre         = Column(String(100), nullable=False)
    email          = Column(String(100), unique=True, nullable=True)
    telefono       = Column(String(20), nullable=True)
    fecha_registro = Column(DateTime, server_default=func.now(), nullable=False)
    activo         = Column(Boolean, default=True, nullable=False)

    usuarios             = relationship("Usuario",           back_populates="cliente", cascade="all, delete")
    facturas             = relationship("Facturacion",       back_populates="cliente", cascade="all, delete")
    cliente_dispositivos = relationship("ClienteDispositivo", back_populates="cliente", cascade="all, delete")
