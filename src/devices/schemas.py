from pydantic import BaseModel

from datetime import datetime

from typing import Optional





class ClientDeviceBase(BaseModel):

    client_id:       int

    location_id:     int

    device_mongo_id: str





class ClientDeviceCreate(ClientDeviceBase):

    pass





class ClientDeviceUpdate(BaseModel):

    location_id:     Optional[int] = None

    device_mongo_id: Optional[str] = None





class ClientDeviceResponse(ClientDeviceBase):

    id:               int

    association_date: datetime



    model_config = {"from_attributes": True} 

