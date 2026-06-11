from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.mysql import get_db
from src.auth.dependencies import get_current_user, require_role
from src.users.models import User, RoleEnum
from src.clients.models import Client
from src.clients.schemas import ClientCreate, ClientUpdate, ClientResponse

router = APIRouter()


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    skip:  int = 0,
    limit: int = 100,
    db:    Session = Depends(get_db),
    _:     User = Depends(require_role(RoleEnum.admin)),
):
    """List all clients. Admin only."""
    return db.query(Client).offset(skip).limit(limit).all()


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id:    int,
    db:           Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single client.
    - Admin: any client.
    - Technician / Viewer: only their own client.
    """
    if current_user.role != RoleEnum.admin and current_user.client_id != client_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return client


@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(
    data: ClientCreate,
    db:   Session = Depends(get_db),
    _:    User = Depends(require_role(RoleEnum.admin)),
):
    """Create a new client. Admin only."""
    if data.email:
        exists = db.query(Client).filter(Client.email == data.email).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    client = Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    data:      ClientUpdate,
    db:        Session = Depends(get_db),
    _:         User = Depends(require_role(RoleEnum.admin)),
):
    """Update a client. Admin only."""
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if data.email and data.email != client.email:
        exists = db.query(Client).filter(Client.email == data.email).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db:        Session = Depends(get_db),
    _:         User = Depends(require_role(RoleEnum.admin)),
):
    """
    Delete a client. Admin only.
    Cascades to users, invoices and client_devices.
    """
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    db.delete(client)
    db.commit()
