"""add field 'is_active' to users model

Revision ID: 92e6d1502830
Revises: 4cbbd9526700
Create Date: 2026-07-17 02:17:43.460612

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "92e6d1502830"
down_revision: Union[str, Sequence[str], None] = "4cbbd9526700"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_active", sa.Boolean(), server_default="true", nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_active")
