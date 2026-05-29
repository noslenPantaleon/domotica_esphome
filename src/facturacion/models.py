import enum
from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class EstadoFacturaEnum(str, enum.Enum):
    pendiente = "pendiente"
    pagada    = "pagada"
    vencida   = "vencida"


class Facturacion(Base):
    __tablename__ = "facturacion"

    factura_id        = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id        = Column(Integer, ForeignKey("clientes.cliente_id", ondelete="CASCADE"), nullable=False)
    fecha_emision     = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    monto             = Column(Numeric(10, 2), nullable=False)
    estado            = Column(Enum(EstadoFacturaEnum), default=EstadoFacturaEnum.pendiente, nullable=False)
    metodo_pago       = Column(String(50), nullable=True)

    cliente = relationship("Cliente", back_populates="facturas")
