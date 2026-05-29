import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class RolEnum(str, enum.Enum):
    admin        = "admin"
    tecnico      = "tecnico"
    visualizador = "visualizador"


class Usuario(Base):
    __tablename__ = "usuarios"

    usuario_id     = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id     = Column(Integer, ForeignKey("clientes.cliente_id", ondelete="CASCADE"), nullable=False)
    nombre         = Column(String(100), nullable=False)
    email          = Column(String(100), unique=True, nullable=False)
    password_hash  = Column(String(255), nullable=False)
    rol            = Column(Enum(RolEnum), nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now(), nullable=False)
    ultimo_login   = Column(DateTime, nullable=True)

    cliente = relationship("Cliente", back_populates="usuarios")
