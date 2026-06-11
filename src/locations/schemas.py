from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class LocationBase(BaseModel):
    country:       str
    district:      Optional[str]     = None
    street:        Optional[str]     = None
    street_number: Optional[int]     = None
    latitude:      Optional[Decimal] = None
    longitude:     Optional[Decimal] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    country:       Optional[str]     = None
    district:      Optional[str]     = None
    street:        Optional[str]     = None
    street_number: Optional[int]     = None
    latitude:      Optional[Decimal] = None
    longitude:     Optional[Decimal] = None


class LocationResponse(LocationBase):
    location_id: int

    model_config = {"from_attributes": True}
