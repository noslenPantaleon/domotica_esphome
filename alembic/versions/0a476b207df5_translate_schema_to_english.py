"""translate_schema_to_english

Revision ID: 0a476b207df5
Revises: 2c0262929936
Create Date: 2026-06-11 17:18:07.561735

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a476b207df5'
down_revision: Union[str, None] = '2c0262929936'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_fks(table_name: str) -> None:
    conn = op.get_bind()
    rows = conn.execute(sa.text("""
        SELECT CONSTRAINT_NAME FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :t AND CONSTRAINT_TYPE = 'FOREIGN KEY'
    """), {"t": table_name}).fetchall()
    for (name,) in rows:
        op.execute(f"ALTER TABLE `{table_name}` DROP FOREIGN KEY `{name}`")


def upgrade() -> None:
    # Drop FKs referencing tables/columns that are about to be renamed
    _drop_fks('usuarios')
    _drop_fks('facturacion')
    _drop_fks('cliente_dispositivos')

    # Rename tables
    op.rename_table('clientes', 'clients')
    op.rename_table('ubicaciones', 'locations')
    op.rename_table('usuarios', 'users')
    op.rename_table('facturacion', 'invoices')
    op.rename_table('cliente_dispositivos', 'client_devices')

    # clients
    op.execute("ALTER TABLE clients CHANGE cliente_id client_id INT NOT NULL AUTO_INCREMENT")
    op.execute("ALTER TABLE clients CHANGE nombre name VARCHAR(100) NOT NULL")
    op.execute("ALTER TABLE clients CHANGE telefono phone VARCHAR(20) NULL")
    op.execute("ALTER TABLE clients CHANGE fecha_registro registration_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
    op.execute("ALTER TABLE clients CHANGE activo active TINYINT(1) NOT NULL")

    # locations
    op.execute("ALTER TABLE locations CHANGE ubicacion_id location_id INT NOT NULL AUTO_INCREMENT")
    op.execute("ALTER TABLE locations CHANGE pais country VARCHAR(100) NOT NULL")
    op.execute("ALTER TABLE locations CHANGE comuna district VARCHAR(100) NULL")
    op.execute("ALTER TABLE locations CHANGE calle street VARCHAR(255) NULL")
    op.execute("ALTER TABLE locations CHANGE numero_calle street_number INT NULL")
    op.execute("ALTER TABLE locations CHANGE latitud latitude NUMERIC(10, 8) NULL")
    op.execute("ALTER TABLE locations CHANGE longitud longitude NUMERIC(11, 8) NULL")

    # users
    op.execute("ALTER TABLE users CHANGE usuario_id user_id INT NOT NULL AUTO_INCREMENT")
    op.execute("ALTER TABLE users CHANGE cliente_id client_id INT NOT NULL")
    op.execute("ALTER TABLE users CHANGE nombre name VARCHAR(100) NOT NULL")
    op.execute("ALTER TABLE users CHANGE fecha_creacion created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
    op.execute("ALTER TABLE users CHANGE ultimo_login last_login DATETIME NULL")
    op.execute("ALTER TABLE users MODIFY rol ENUM('admin', 'tecnico', 'visualizador', 'technician', 'viewer') NOT NULL")
    op.execute("UPDATE users SET rol = 'technician' WHERE rol = 'tecnico'")
    op.execute("UPDATE users SET rol = 'viewer' WHERE rol = 'visualizador'")
    op.execute("ALTER TABLE users CHANGE rol role ENUM('admin', 'technician', 'viewer') NOT NULL")

    # invoices
    op.execute("ALTER TABLE invoices CHANGE factura_id invoice_id INT NOT NULL AUTO_INCREMENT")
    op.execute("ALTER TABLE invoices CHANGE cliente_id client_id INT NOT NULL")
    op.execute("ALTER TABLE invoices CHANGE fecha_emision issue_date DATE NOT NULL")
    op.execute("ALTER TABLE invoices CHANGE fecha_vencimiento due_date DATE NOT NULL")
    op.execute("ALTER TABLE invoices CHANGE monto amount NUMERIC(10, 2) NOT NULL")
    op.execute("ALTER TABLE invoices CHANGE metodo_pago payment_method VARCHAR(50) NULL")
    op.execute("ALTER TABLE invoices MODIFY estado ENUM('pendiente', 'pagada', 'vencida', 'pending', 'paid', 'overdue') NOT NULL DEFAULT 'pending'")
    op.execute("UPDATE invoices SET estado = 'pending' WHERE estado = 'pendiente'")
    op.execute("UPDATE invoices SET estado = 'paid' WHERE estado = 'pagada'")
    op.execute("UPDATE invoices SET estado = 'overdue' WHERE estado = 'vencida'")
    op.execute("ALTER TABLE invoices CHANGE estado status ENUM('pending', 'paid', 'overdue') NOT NULL DEFAULT 'pending'")

    # client_devices
    op.execute("ALTER TABLE client_devices CHANGE cliente_id client_id INT NOT NULL")
    op.execute("ALTER TABLE client_devices CHANGE ubicacion_id location_id INT NOT NULL")
    op.execute("ALTER TABLE client_devices CHANGE dispositivo_mongo_id device_mongo_id VARCHAR(24) NOT NULL COMMENT 'ID of the document in MongoDB'")
    op.execute("ALTER TABLE client_devices CHANGE fecha_asociacion association_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")

    # Recreate FKs with renamed columns/tables
    op.create_foreign_key('fk_users_client_id', 'users', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.create_foreign_key('fk_invoices_client_id', 'invoices', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.create_foreign_key('fk_client_devices_client_id', 'client_devices', 'clients', ['client_id'], ['client_id'], ondelete='CASCADE')
    op.create_foreign_key('fk_client_devices_location_id', 'client_devices', 'locations', ['location_id'], ['location_id'], ondelete='CASCADE')


def downgrade() -> None:
    _drop_fks('users')
    _drop_fks('invoices')
    _drop_fks('client_devices')

    # client_devices
    op.execute("ALTER TABLE client_devices CHANGE client_id cliente_id INT NOT NULL")
    op.execute("ALTER TABLE client_devices CHANGE location_id ubicacion_id INT NOT NULL")
    op.execute("ALTER TABLE client_devices CHANGE device_mongo_id dispositivo_mongo_id VARCHAR(24) NOT NULL COMMENT 'ID del documento en MongoDB'")
    op.execute("ALTER TABLE client_devices CHANGE association_date fecha_asociacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")

    # invoices
    op.execute("ALTER TABLE invoices MODIFY status ENUM('pendiente', 'pagada', 'vencida', 'pending', 'paid', 'overdue') NOT NULL DEFAULT 'pending'")
    op.execute("UPDATE invoices SET status = 'pendiente' WHERE status = 'pending'")
    op.execute("UPDATE invoices SET status = 'pagada' WHERE status = 'paid'")
    op.execute("UPDATE invoices SET status = 'vencida' WHERE status = 'overdue'")
    op.execute("ALTER TABLE invoices CHANGE status estado ENUM('pendiente', 'pagada', 'vencida') NOT NULL DEFAULT 'pendiente'")
    op.execute("ALTER TABLE invoices CHANGE invoice_id factura_id INT NOT NULL AUTO_INCREMENT")
    op.execute("ALTER TABLE invoices CHANGE client_id cliente_id INT NOT NULL")
    op.execute("ALTER TABLE invoices CHANGE issue_date fecha_emision DATE NOT NULL")
    op.execute("ALTER TABLE invoices CHANGE due_date fecha_vencimiento DATE NOT NULL")
    op.execute("ALTER TABLE invoices CHANGE amount monto NUMERIC(10, 2) NOT NULL")
    op.execute("ALTER TABLE invoices CHANGE payment_method metodo_pago VARCHAR(50) NULL")

    # users
    op.execute("ALTER TABLE users MODIFY role ENUM('admin', 'tecnico', 'visualizador', 'technician', 'viewer') NOT NULL")
    op.execute("UPDATE users SET role = 'tecnico' WHERE role = 'technician'")
    op.execute("UPDATE users SET role = 'visualizador' WHERE role = 'viewer'")
    op.execute("ALTER TABLE users CHANGE role rol ENUM('admin', 'tecnico', 'visualizador') NOT NULL")
    op.execute("ALTER TABLE users CHANGE user_id usuario_id INT NOT NULL AUTO_INCREMENT")
    op.execute("ALTER TABLE users CHANGE client_id cliente_id INT NOT NULL")
    op.execute("ALTER TABLE users CHANGE name nombre VARCHAR(100) NOT NULL")
    op.execute("ALTER TABLE users CHANGE created_at fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
    op.execute("ALTER TABLE users CHANGE last_login ultimo_login DATETIME NULL")

    # locations
    op.execute("ALTER TABLE locations CHANGE location_id ubicacion_id INT NOT NULL AUTO_INCREMENT")
    op.execute("ALTER TABLE locations CHANGE country pais VARCHAR(100) NOT NULL")
    op.execute("ALTER TABLE locations CHANGE district comuna VARCHAR(100) NULL")
    op.execute("ALTER TABLE locations CHANGE street calle VARCHAR(255) NULL")
    op.execute("ALTER TABLE locations CHANGE street_number numero_calle INT NULL")
    op.execute("ALTER TABLE locations CHANGE latitude latitud NUMERIC(10, 8) NULL")
    op.execute("ALTER TABLE locations CHANGE longitude longitud NUMERIC(11, 8) NULL")

    # clients
    op.execute("ALTER TABLE clients CHANGE client_id cliente_id INT NOT NULL AUTO_INCREMENT")
    op.execute("ALTER TABLE clients CHANGE name nombre VARCHAR(100) NOT NULL")
    op.execute("ALTER TABLE clients CHANGE phone telefono VARCHAR(20) NULL")
    op.execute("ALTER TABLE clients CHANGE registration_date fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP")
    op.execute("ALTER TABLE clients CHANGE active activo TINYINT(1) NOT NULL")

    # Rename tables back
    op.rename_table('client_devices', 'cliente_dispositivos')
    op.rename_table('invoices', 'facturacion')
    op.rename_table('users', 'usuarios')
    op.rename_table('locations', 'ubicaciones')
    op.rename_table('clients', 'clientes')

    # Recreate original FKs
    op.create_foreign_key(None, 'usuarios', 'clientes', ['cliente_id'], ['cliente_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'facturacion', 'clientes', ['cliente_id'], ['cliente_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'cliente_dispositivos', 'clientes', ['cliente_id'], ['cliente_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'cliente_dispositivos', 'ubicaciones', ['ubicacion_id'], ['ubicacion_id'], ondelete='CASCADE')
