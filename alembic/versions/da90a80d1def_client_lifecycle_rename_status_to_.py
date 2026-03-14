"""client lifecycle rename status to client_status

Revision ID: da90a80d1def
Revises: 0f0e1d2c3b4a
Create Date: 2026-01-12 10:35:47.047561+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da90a80d1def'
down_revision: Union[str, Sequence[str], None] = '0f0e1d2c3b4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "clients",
        "status",
        new_column_name="client_status",
        existing_type=sa.String(),
        nullable=False,
        server_default="invited",
    )


def downgrade():
    op.alter_column(
        "clients",
        "client_status",
        new_column_name="status",
        existing_type=sa.String(),
        nullable=False,
    )
