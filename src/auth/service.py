from datetime import datetime, timedelta
from jose import jwt
from src.config.settings import settings

# Importamos desde el núcleo de seguridad
from src.core.security import get_password_hash, verify_password

# ELIMINAMOS las funciones get_password_hash y verify_password locales 
# porque ya las estás importando de security.py. 
# Si necesitas usarlas en otros archivos, impórtalas directamente de 'src.core.security'.

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload["exp"] = expire
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])