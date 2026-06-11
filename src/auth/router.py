from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.config.settings import settings
from src.database.mysql import get_db
from src.users.models import User
from src.users.schemas import UserResponse
from src.auth.schemas import Token
from src.auth.service import verify_password, create_access_token
from src.auth.dependencies import get_current_user

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db:        Session = Depends(get_db),
):
    """
    Login with email + password.
    The 'username' field in the form accepts the user's email.
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={
            "sub":       user.email,
            "user_id":   user.user_id,
            "client_id": user.client_id,
            "role":      user.role.value,
        },
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """Returns the currently authenticated user."""
    return current_user
