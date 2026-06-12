from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.database.mysql import get_db
from src.database.mongodb import get_mongo_db
from src.auth.dependencies import get_current_user, require_role
from src.users.models import User, RoleEnum
from src.clients.models import Client
from src.locations.models import Location
from src.devices.models import ClientDevice
from src.devices.schemas import ClientDeviceCreate, ClientDeviceUpdate, ClientDeviceResponse
from src.devices.mongo_schemas import DeviceMongoCreate, DeviceMongoResponse

router = APIRouter()


@router.get("/", response_model=List[ClientDeviceResponse])
def list_client_devices(
    skip:  int = 0,
    limit: int = 100,
    db:    Session = Depends(get_db),
    _:     User = Depends(require_role(RoleEnum.admin)),
):
    """List all client devices. Admin only."""
    return db.query(ClientDevice).offset(skip).limit(limit).all()


@router.post("/mongo", response_model=DeviceMongoResponse, status_code=status.HTTP_201_CREATED)
async def create_device_document(
    data:     DeviceMongoCreate,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db),
    _:        User = Depends(require_role(RoleEnum.admin)),
):
    """Create a device document in MongoDB. Admin only."""
    doc = data.model_dump(by_alias=True)
    if await mongo_db.devices.find_one({"_id": doc["_id"]}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device already exists")

    await mongo_db.devices.insert_one(doc)
    return doc


@router.get("/mongo", response_model=List[DeviceMongoResponse])
async def list_device_documents(
    client_id:    Optional[int] = None,
    mongo_db:     AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    """
    List device documents.
    - Admin: all devices, optionally filtered by client_id.
    - Technician / Viewer: only devices belonging to their own client.
    """
    if current_user.role != RoleEnum.admin:
        client_id = current_user.client_id

    query = {} if client_id is None else {"client_id": client_id}
    return [doc async for doc in mongo_db.devices.find(query)]


@router.get("/mongo/{device_id}", response_model=DeviceMongoResponse)
async def get_device_document(
    device_id:    str,
    mongo_db:     AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a device document by its Mongo id.
    - Admin: any device.
    - Technician / Viewer: only their own client's device.
    """
    doc = await mongo_db.devices.find_one({"_id": device_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if current_user.role != RoleEnum.admin and current_user.client_id != doc.get("client_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return doc


@router.get("/mongo/{device_id}/readings")
async def get_device_readings(
    device_id:    str,
    limit:        int = 100,
    mongo_db:     AsyncIOMotorDatabase = Depends(get_mongo_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the most recent sensor readings for a device (time-series log).
    - Admin: any device.
    - Technician / Viewer: only their own client's device.
    """
    doc = await mongo_db.devices.find_one({"_id": device_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if current_user.role != RoleEnum.admin and current_user.client_id != doc.get("client_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    cursor = mongo_db.sensor_readings.find({"device_id": device_id}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return [reading async for reading in cursor]


@router.get("/{device_id}", response_model=ClientDeviceResponse)
def get_client_device(
    device_id:    int,
    db:           Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single client device.
    - Admin: any device.
    - Technician / Viewer: only devices belonging to their own client.
    """
    device = db.query(ClientDevice).filter(ClientDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if current_user.role != RoleEnum.admin and current_user.client_id != device.client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return device


@router.post("/", response_model=ClientDeviceResponse, status_code=status.HTTP_201_CREATED)
def create_client_device(
    data: ClientDeviceCreate,
    db:   Session = Depends(get_db),
    _:    User = Depends(require_role(RoleEnum.admin)),
):
    """Create a new client device. Admin only."""
    if not db.query(Client).filter(Client.client_id == data.client_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if not db.query(Location).filter(Location.location_id == data.location_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    device = ClientDevice(**data.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.put("/{device_id}", response_model=ClientDeviceResponse)
def update_client_device(
    device_id: int,
    data:      ClientDeviceUpdate,
    db:        Session = Depends(get_db),
    _:         User = Depends(require_role(RoleEnum.admin)),
):
    """Update a client device. Admin only."""
    device = db.query(ClientDevice).filter(ClientDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if data.location_id is not None:
        if not db.query(Location).filter(Location.location_id == data.location_id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client_device(
    device_id: int,
    db:        Session = Depends(get_db),
    _:         User = Depends(require_role(RoleEnum.admin)),
):
    """Delete a client device. Admin only."""
    device = db.query(ClientDevice).filter(ClientDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    db.delete(device)
    db.commit()
