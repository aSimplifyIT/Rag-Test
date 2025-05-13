"""file-table

Revision ID: 1e7e1629473b
Revises: b1294ffc9328
Create Date: 2025-05-13 15:34:08.229588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e7e1629473b'
down_revision: Union[str, None] = 'b1294ffc9328'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
