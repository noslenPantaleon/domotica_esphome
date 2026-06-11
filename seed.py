"""
Bootstrap script — run once to create the first client and admin user.
Usage:
    python seed.py
"""
from src.database.mysql import SessionLocal

# All models must be imported so SQLAlchemy can resolve relationships
from src.clients.models import Client
from src.locations.models import Location
from src.users.models import User, RoleEnum
from src.billing.models import Invoice
from src.devices.models import ClientDevice

from src.auth.service import get_password_hash

# ── Configure your first admin here ─────────────────────────────────────────
CLIENT_NAME    = "Mi Empresa"
ADMIN_NAME     = "Administrador"
ADMIN_EMAIL    = "admin@domotic.com"
ADMIN_PASSWORD = "admin1234"
# ─────────────────────────────────────────────────────────────────────────────

db = SessionLocal()

try:
    # Check if already seeded
    if db.query(User).filter(User.email == ADMIN_EMAIL).first():
        print(f"User '{ADMIN_EMAIL}' already exists — skipping seed.")
        exit(0)

    # 1. Create client
    client = Client(name=CLIENT_NAME, active=True)
    db.add(client)
    db.flush()  # get client_id without committing

    # 2. Create admin user
    admin = User(
        client_id     = client.client_id,
        name          = ADMIN_NAME,
        email         = ADMIN_EMAIL,
        password_hash = get_password_hash(ADMIN_PASSWORD),
        role          = RoleEnum.admin,
    )
    db.add(admin)
    db.commit()

    print("Seed completed:")
    print(f"  Client   id={client.client_id}  name='{client.name}'")
    print(f"  Admin    id={admin.user_id}      email='{admin.email}'")
    print(f"  Password {ADMIN_PASSWORD}  (change this after first login)")

except Exception as e:
    db.rollback()
    print(f"Seed failed: {e}")
finally:
    db.close()
