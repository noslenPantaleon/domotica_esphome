from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.mysql import get_db
from src.auth.dependencies import get_current_user, require_role
from src.users.models import User, RoleEnum
from src.clients.models import Client
from src.locations.models import Location
from src.devices.models import ClientDevice
from src.devices.schemas import ClientDeviceCreate, ClientDeviceUpdate, ClientDeviceResponse

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
