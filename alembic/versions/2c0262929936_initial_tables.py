"""initial_tables

Revision ID: 2c0262929936
Revises:
Create Date: 2026-05-29 15:04:08.057252

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c0262929936'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'clientes',
        sa.Column('cliente_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('telefono', sa.String(length=20), nullable=True),
        sa.Column('fecha_registro', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('cliente_id'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'ubicaciones',
        sa.Column('ubicacion_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('pais', sa.String(length=100), nullable=False),
        sa.Column('comuna', sa.String(length=100), nullable=True),
        sa.Column('calle', sa.String(length=255), nullable=True),
        sa.Column('numero_calle', sa.Integer(), nullable=True),
        sa.Column('latitud', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitud', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.PrimaryKeyConstraint('ubicacion_id'),
    )

    op.create_table(
        'usuarios',
        sa.Column('usuario_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('rol', sa.Enum('admin', 'tecnico', 'visualizador', name='rolenum'), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('ultimo_login', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.cliente_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('usuario_id'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'facturacion',
        sa.Column('factura_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('fecha_emision', sa.Date(), nullable=False),
        sa.Column('fecha_vencimiento', sa.Date(), nullable=False),
        sa.Column('monto', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('estado', sa.Enum('pendiente', 'pagada', 'vencida', name='estadofacturaenum'), nullable=False),
        sa.Column('metodo_pago', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.cliente_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('factura_id'),
    )

    op.create_table(
        'cliente_dispositivos',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('ubicacion_id', sa.Integer(), nullable=False),
        sa.Column('dispositivo_mongo_id', sa.String(length=24), nullable=False, comment='ID del documento en MongoDB'),
        sa.Column('fecha_asociacion', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.cliente_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ubicacion_id'], ['ubicaciones.ubicacion_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_mongo_id', 'cliente_dispositivos', ['dispositivo_mongo_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_mongo_id', table_name='cliente_dispositivos')
    op.drop_table('cliente_dispositivos')
    op.drop_table('facturacion')
    op.drop_table('usuarios')
    op.drop_table('ubicaciones')
    op.drop_table('clientes')
