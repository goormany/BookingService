"""set field descritions form rooms in nullable

Revision ID: af89b97af4de
Revises: 7fa1b90715e8
Create Date: 2026-07-12 21:52:43.205905

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "af89b97af4de"
down_revision: Union[str, Sequence[str], None] = "7fa1b90715e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("rooms", "description", existing_type=sa.VARCHAR(), nullable=True)


def downgrade() -> None:
    op.alter_column("rooms", "description", existing_type=sa.VARCHAR(), nullable=False)
