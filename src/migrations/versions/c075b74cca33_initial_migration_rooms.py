"""initial migration rooms

Revision ID: c075b74cca33
Revises: ff22527b70fe
Create Date: 2025-11-21 15:48:44.329937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c075b74cca33'
down_revision: Union[str, Sequence[str], None] = 'ff22527b70fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('rooms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('hotel_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('rooms')
