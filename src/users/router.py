from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import bcrypt  # 👈 Usamos la librería directa de forma nativa

from src.database.mysql import get_db
from src.users.models import User, RoleEnum
from src.users.schemas import UserResponse  
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserCreateForm(BaseModel):
    name: str
    email: EmailStr
    password: str
    client_id: int
    role: str = "viewer"

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreateForm, db: Session = Depends(get_db)):
    """Crea un usuario en MySQL aplicando hash directo con bcrypt."""
    
    # 1. Verificar si el email ya está registrado
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado."
        )

    # 2. Mapear el rol del string al Enum
    try:
        user_role = RoleEnum[payload.role]
    except KeyError:
        user_role = RoleEnum.viewer

    # 3. Generar el HASH de la contraseña con bcrypt puro
    # El password debe convertirse a bytes (.encode('utf-8')) para procesarse
    password_bytes = payload.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    # 4. Crear la instancia para la DB
    new_user = User(
        client_id=payload.client_id,
        name=payload.name,
        email=payload.email,
        password_hash=hashed_password, # Guardado seguro
        role=user_role
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en la base de datos: {str(e)}"
        )


@router.get("/", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """Retorna el catálogo completo de usuarios registrados en MySQL."""
    users = db.query(User).all()
    return users