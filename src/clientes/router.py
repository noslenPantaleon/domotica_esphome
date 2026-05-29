from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.mysql import get_db
from src.auth.dependencies import get_current_user, require_role
from src.usuarios.models import Usuario, RolEnum
from src.clientes.models import Cliente
from src.clientes.schemas import ClienteCreate, ClienteUpdate, ClienteResponse

router = APIRouter()


@router.get("/", response_model=List[ClienteResponse])
def list_clientes(
    skip:  int = 0,
    limit: int = 100,
    db:    Session = Depends(get_db),
    _:     Usuario = Depends(require_role(RolEnum.admin)),
):
    """List all clients. Admin only."""
    return db.query(Cliente).offset(skip).limit(limit).all()


@router.get("/{cliente_id}", response_model=ClienteResponse)
def get_cliente(
    cliente_id:   int,
    db:           Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Get a single client.
    - Admin: any client.
    - Tecnico / Visualizador: only their own client.
    """
    if current_user.rol != RolEnum.admin and current_user.cliente_id != cliente_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    cliente = db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    return cliente


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def create_cliente(
    data: ClienteCreate,
    db:   Session = Depends(get_db),
    _:    Usuario = Depends(require_role(RolEnum.admin)),
):
    """Create a new client. Admin only."""
    if data.email:
        exists = db.query(Cliente).filter(Cliente.email == data.email).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    cliente = Cliente(**data.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
def update_cliente(
    cliente_id: int,
    data:       ClienteUpdate,
    db:         Session = Depends(get_db),
    _:          Usuario = Depends(require_role(RolEnum.admin)),
):
    """Update a client. Admin only."""
    cliente = db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    if data.email and data.email != cliente.email:
        exists = db.query(Cliente).filter(Cliente.email == data.email).first()
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already in use")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cliente, field, value)

    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cliente(
    cliente_id: int,
    db:         Session = Depends(get_db),
    _:          Usuario = Depends(require_role(RolEnum.admin)),
):
    """
    Delete a client. Admin only.
    Cascades to usuarios, facturas and cliente_dispositivos.
    """
    cliente = db.query(Cliente).filter(Cliente.cliente_id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")

    db.delete(cliente)
    db.commit()
