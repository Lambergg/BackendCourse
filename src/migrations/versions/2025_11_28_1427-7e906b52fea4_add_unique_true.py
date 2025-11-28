"""add unique=True

Revision ID: 7e906b52fea4
Revises: aa85c5636258
Create Date: 2025-11-28 14:27:44.913068

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



revision: str = "7e906b52fea4"
down_revision: Union[str, Sequence[str], None] = "aa85c5636258"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "users", type_="unique")
