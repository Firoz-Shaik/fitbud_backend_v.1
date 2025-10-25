"""enable_uuid_extension

Revision ID: 1_enable_uuid_extension
Revises: dba6708623df
Create Date: 2025-08-31 06:25:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1_enable_uuid_extension'
down_revision: Union[str, None] = '8ed3bb18f0e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')


def downgrade() -> None:
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')