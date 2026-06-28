from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.mysql import get_db
from src.auth.dependencies import get_current_user, require_role
from src.users.models import User, RoleEnum
from src.users.schemas import UserCreate, UserUpdate, UserResponse
from src.core.security import get_password_hash

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: User = Depends(require_role(RoleEnum.admin))):
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verificación de permisos
    if current_user.role != RoleEnum.admin and current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), _: User = Depends(require_role(RoleEnum.admin))):
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user_data = data.model_dump()
    # Reemplaza la contraseña plana por su hash antes de guardar.
    user_data["password_hash"] = get_password_hash(user_data.pop("password"))
    
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), _: User = Depends(require_role(RoleEnum.admin))):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "password":
            setattr(user, "password_hash", get_password_hash(value))
        else:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(require_role(RoleEnum.admin))):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()