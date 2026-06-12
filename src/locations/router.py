from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.mysql import get_db
from src.auth.dependencies import get_current_user, require_role
from src.users.models import User, RoleEnum
from src.locations.models import Location
from src.locations.schemas import LocationCreate, LocationUpdate, LocationResponse

router = APIRouter()


@router.get("/", response_model=List[LocationResponse])
def list_locations(
    skip:  int = 0,
    limit: int = 100,
    db:    Session = Depends(get_db),
    _:     User = Depends(require_role(RoleEnum.admin)),
):
    """List all locations. Admin only."""
    return db.query(Location).offset(skip).limit(limit).all()


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: int,
    db:           Session = Depends(get_db),
    _:            User = Depends(get_current_user),
):
    """Get a single location."""
    location = db.query(Location).filter(Location.location_id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(
    data: LocationCreate,
    db:   Session = Depends(get_db),
    _:    User = Depends(require_role(RoleEnum.admin)),
):
    """Create a new location. Admin only."""
    location = Location(**data.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(
    location_id: int,
    data:         LocationUpdate,
    db:           Session = Depends(get_db),
    _:            User = Depends(require_role(RoleEnum.admin)),
):
    """Update a location. Admin only."""
    location = db.query(Location).filter(Location.location_id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(location, field, value)

    db.commit()
    db.refresh(location)
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(
    location_id: int,
    db:           Session = Depends(get_db),
    _:            User = Depends(require_role(RoleEnum.admin)),
):
    """
    Delete a location. Admin only.
    Cascades to client_devices.
    """
    location = db.query(Location).filter(Location.location_id == location_id).first()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")

    db.delete(location)
    db.commit()
