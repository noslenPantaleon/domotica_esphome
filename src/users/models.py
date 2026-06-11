import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.database.mysql import Base


class RoleEnum(str, enum.Enum):
    admin     = "admin"
    technician = "technician"
    viewer    = "viewer"


class User(Base):
    __tablename__ = "users"

    user_id    = Column(Integer, primary_key=True, autoincrement=True)
    client_id  = Column(Integer, ForeignKey("clients.client_id", ondelete="CASCADE"), nullable=False)
    name       = Column(String(100), nullable=False)
    email      = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role       = Column(Enum(RoleEnum), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)

    client = relationship("Client", back_populates="users")
