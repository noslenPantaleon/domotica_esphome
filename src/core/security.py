# este archivo fue creado para manejar la seguridad de las contraseñas, utilizando Passlib para el hashing y verificación de contraseñas.
# ya que Passlib es una biblioteca de Python que proporciona una forma fácil de manejar el hashing de contraseñas, 
# incluyendo la verificación y generación de hashes seguros. En este archivo, 
# se define una función para verificar contraseñas y otra para generar hashes de contraseñas utilizando el algoritmo Bcrypt, 
# que es conocido por su seguridad y resistencia a ataques de fuerza bruta.

from passlib.context import CryptContext

# Ajustamos la configuración para que passlib gestione el backend de forma más estricta
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__ident="2a"  # Forzamos una identificación de versión compatible
)

def get_password_hash(password: str) -> str:
    # Truncar a 72 bytes es una excelente práctica para bcrypt
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
        
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncar también durante la verificación para evitar errores de longitud
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
        
    return pwd_context.verify(plain_password, hashed_password)