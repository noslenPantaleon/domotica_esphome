from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class Ubicacion(Base):
    __tablename__ = "ubicaciones"

    ubicacion_id  = Column(Integer, primary_key=True, autoincrement=True)
    pais          = Column(String(100), nullable=False)
    comuna        = Column(String(100), nullable=True)
    calle         = Column(String(255), nullable=True)
    numero_calle  = Column(Integer, nullable=True)
    latitud       = Column(Numeric(10, 8), nullable=True)
    longitud      = Column(Numeric(11, 8), nullable=True)

    cliente_dispositivos = relationship("ClienteDispositivo", back_populates="ubicacion", cascade="all, delete")
