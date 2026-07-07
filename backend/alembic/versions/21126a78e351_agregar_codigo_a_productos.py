"""agregar codigo a productos

Revision ID: 21126a78e351
Revises: 867badc32e0b
Create Date: 2026-07-06 13:32:22.686803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21126a78e351'
down_revision: Union[str, Sequence[str], None] = '867badc32e0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # PASO 1: Agregar columna como NULLABLE primero
    op.add_column('productos', sa.Column('codigo', sa.String(length=50), nullable=True))
    
    # PASO 2: Generar códigos temporales para productos existentes
    # Formato: "PROD-" + ID del producto (ej: PROD-1, PROD-2, etc.)
    op.execute("""
        UPDATE productos 
        SET codigo = 'PROD-' || CAST(id AS VARCHAR) 
        WHERE codigo IS NULL
    """)
    
    # PASO 3: Ahora sí, hacer la columna NOT NULL
    op.alter_column(
        'productos', 
        'codigo',
        existing_type=sa.String(length=50),
        nullable=False
    )
    
    # PASO 4: Crear índice único
    op.create_index(op.f('ix_productos_codigo'), 'productos', ['codigo'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_productos_codigo'), table_name='productos')
    op.drop_column('productos', 'codigo')