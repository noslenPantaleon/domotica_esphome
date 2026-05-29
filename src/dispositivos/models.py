from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class ClienteDispositivo(Base):
    __tablename__ = "cliente_dispositivos"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id           = Column(Integer, ForeignKey("clientes.cliente_id", ondelete="CASCADE"), nullable=False)
    ubicacion_id         = Column(Integer, ForeignKey("ubicaciones.ubicacion_id", ondelete="CASCADE"), nullable=False)
    dispositivo_mongo_id = Column(String(24), nullable=False, comment="ID del documento en MongoDB")
    fecha_asociacion     = Column(DateTime, server_default=func.now(), nullable=False)

    cliente   = relationship("Cliente",   back_populates="cliente_dispositivos")
    ubicacion = relationship("Ubicacion", back_populates="cliente_dispositivos")

    __table_args__ = (
        Index("idx_mongo_id", "dispositivo_mongo_id"),
    )
