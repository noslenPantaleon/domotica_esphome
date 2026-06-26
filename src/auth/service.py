from datetime import datetime, timedelta
from jose import jwt
from src.config.settings import settings

# Importamos las funciones que gestionan la seguridad con argon2
from src.core.security import get_password_hash, verify_password

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload["exp"] = expire
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

# Ya no necesitamos definir get_password_hash y verify_password aquí,
# porque ahora las importamos y usamos directamente desde src.core.security.
