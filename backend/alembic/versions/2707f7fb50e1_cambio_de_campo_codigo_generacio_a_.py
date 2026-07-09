"""Cambio de campo codigo_generacio a origen en tabla ingreso

Revision ID: 2707f7fb50e1
Revises: 2190e9a3e100
Create Date: 2026-07-08 14:21:12.169199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2707f7fb50e1'
down_revision: Union[str, Sequence[str], None] = '2190e9a3e100'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
