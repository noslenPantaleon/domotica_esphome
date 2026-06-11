from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class ClientDevice(Base):
    __tablename__ = "client_devices"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    client_id       = Column(Integer, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
    location_id     = Column(Integer, ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False)
    device_mongo_id = Column(String(24), nullable=False, comment="ID of the document in MongoDB")
    association_date = Column(DateTime, server_default=func.now(), nullable=False)

    client   = relationship("Client",   back_populates="client_devices")
    location = relationship("Location", back_populates="client_devices")

    __table_args__ = (
        Index("idx_mongo_id", "device_mongo_id"),
    )
