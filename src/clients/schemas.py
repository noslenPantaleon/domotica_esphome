from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class ClientBase(BaseModel):
    name:   str
    email:  Optional[EmailStr] = None
    phone:  Optional[str]      = None
    active: bool                = True


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name:   Optional[str]      = None
    email:  Optional[EmailStr] = None
    phone:  Optional[str]      = None
    active: Optional[bool]     = None


class ClientResponse(ClientBase):
    client_id:         int
    registration_date: datetime

    model_config = {"from_attributes": True}
