from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from src.database.mysql import get_db
from src.usuarios.models import Usuario, RolEnum
from src.auth.service import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db:    Session = Depends(get_db),
) -> Usuario:
    try:
        payload    = decode_access_token(token)
        usuario_id = payload.get("usuario_id")
        if usuario_id is None:
            raise _401
    except JWTError:
        raise _401

    user = db.query(Usuario).filter(Usuario.usuario_id == usuario_id).first()
    if user is None:
        raise _401
    return user


def require_role(*roles: RolEnum):
    """Factory — use as: Depends(require_role('admin', 'tecnico'))"""
    def _check(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.rol.value}' is not allowed here",
            )
        return current_user
    return _check
