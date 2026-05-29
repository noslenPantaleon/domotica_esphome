"""
Bootstrap script — run once to create the first client and admin user.
Usage:
    python seed.py
"""
from src.database.mysql import SessionLocal

# All models must be imported so SQLAlchemy can resolve relationships
from src.clientes.models import Cliente
from src.ubicaciones.models import Ubicacion
from src.usuarios.models import Usuario, RolEnum
from src.facturacion.models import Facturacion
from src.dispositivos.models import ClienteDispositivo

from src.auth.service import get_password_hash

# ── Configure your first admin here ─────────────────────────────────────────
CLIENTE_NOMBRE = "Mi Empresa"
ADMIN_NOMBRE   = "Administrador"
ADMIN_EMAIL    = "admin@domotic.com"
ADMIN_PASSWORD = "admin1234"
# ─────────────────────────────────────────────────────────────────────────────

db = SessionLocal()

try:
    # Check if already seeded
    if db.query(Usuario).filter(Usuario.email == ADMIN_EMAIL).first():
        print(f"User '{ADMIN_EMAIL}' already exists — skipping seed.")
        exit(0)

    # 1. Create client
    cliente = Cliente(nombre=CLIENTE_NOMBRE, activo=True)
    db.add(cliente)
    db.flush()  # get cliente_id without committing

    # 2. Create admin user
    admin = Usuario(
        cliente_id    = cliente.cliente_id,
        nombre        = ADMIN_NOMBRE,
        email         = ADMIN_EMAIL,
        password_hash = get_password_hash(ADMIN_PASSWORD),
        rol           = RolEnum.admin,
    )
    db.add(admin)
    db.commit()

    print("Seed completed:")
    print(f"  Client   id={cliente.cliente_id}  nombre='{cliente.nombre}'")
    print(f"  Admin    id={admin.usuario_id}    email='{admin.email}'")
    print(f"  Password {ADMIN_PASSWORD}  (change this after first login)")

except Exception as e:
    db.rollback()
    print(f"Seed failed: {e}")
finally:
    db.close()
