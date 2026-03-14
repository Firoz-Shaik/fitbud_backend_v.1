"""Make clients.client_user_id nullable to support invite workflow.

Revision ID: 0f0e1d2c3b4a
Revises: 9c7b5a3e1f0d
Create Date: 2026-01-07
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0f0e1d2c3b4a"
down_revision: Union[str, None] = "9c7b5a3e1f0d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "clients",
        "client_user_id",
        existing_type=postgresql.UUID(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "clients",
        "client_user_id",
        existing_type=postgresql.UUID(),
        nullable=False,
    )


