# este archivo fue creado para manejar la seguridad de las contraseñas, utilizando Passlib para el hashing y verificación de contraseñas.
# ya que Passlib es una biblioteca de Python que proporciona una forma fácil de manejar el hashing de contraseñas, 
# incluyendo la verificación y generación de hashes seguros. En este archivo, 
# se define una función para verificar contraseñas y otra para generar hashes de contraseñas utilizando el algoritmo Bcrypt, 
# que es conocido por su seguridad y resistencia a ataques de fuerza bruta.

# [MODIFICACIÓN 2026-06-25]: Se cambió bcrypt por argon2 debido a 
# incompatibilidades de passlib en Python 3.13. 
# Se eliminó la dependencia de bcrypt para mayor estabilidad.

from passlib.context import CryptContext

# Usamos argon2 como esquema principal, es moderno y sin las limitaciones de bcrypt
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Genera un hash seguro usando Argon2."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra un hash existente."""
    return pwd_context.verify(plain_password, hashed_password)