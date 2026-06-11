from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from src.users.models import RoleEnum


class UserBase(BaseModel):
    name:      str
    email:     EmailStr
    role:      RoleEnum
    client_id: int


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name:     Optional[str]      = None
    email:    Optional[EmailStr] = None
    role:     Optional[RoleEnum] = None
    password: Optional[str]      = None


class UserResponse(UserBase):
    user_id:    int
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}
