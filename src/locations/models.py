from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class Location(Base):
    __tablename__ = "locations"

    location_id   = Column(Integer, primary_key=True, autoincrement=True)
    country       = Column(String(100), nullable=False)
    district      = Column(String(100), nullable=True)
    street        = Column(String(255), nullable=True)
    street_number = Column(Integer, nullable=True)
    latitude      = Column(Numeric(10, 8), nullable=True)
    longitude     = Column(Numeric(11, 8), nullable=True)

    client_devices = relationship("ClientDevice", back_populates="location", cascade="all, delete")
