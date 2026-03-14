"""fix client status constraint

Revision ID: ba6c5f27bacc
Revises: da90a80d1def
Create Date: 2026-02-28 11:24:09.159184+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba6c5f27bacc'
down_revision: Union[str, Sequence[str], None] = 'da90a80d1def'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint("clients_status_check", "clients", type_="check")
    op.create_check_constraint(
        "clients_status_check",
        "clients",
        "client_status IN ('invited','active','paused','archived')"
    )


def downgrade():
    op.drop_constraint("clients_status_check", "clients", type_="check")
    op.create_check_constraint(
        "clients_status_check",
        "clients",
        "client_status IN ('invited','active','inactive')"
    )
