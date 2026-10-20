"""add content column to post table

Revision ID: f90fa9e41806
Revises: ac5ffa481c51
Create Date: 2026-10-19 16:29:00.983068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f90fa9e41806'
down_revision: Union[str, Sequence[str], None] = 'ac5ffa481c51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts', 'content')
    pass
