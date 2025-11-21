"""initial migration

Revision ID: ff22527b70fe
Revises: 
Create Date: 2025-11-21 14:56:29.533706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff22527b70fe'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('hotels',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('hotels')

