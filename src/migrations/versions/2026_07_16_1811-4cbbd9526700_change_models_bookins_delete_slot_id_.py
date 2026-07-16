"""change models bookins: delete slot_id, add start\end_time

Revision ID: 4cbbd9526700
Revises: af89b97af4de
Create Date: 2026-07-16 18:11:31.860263

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "4cbbd9526700"
down_revision: Union[str, Sequence[str], None] = "af89b97af4de"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "bookings",
        sa.Column("start_time", sa.Time(timezone=True), nullable=False),
    )
    op.add_column(
        "bookings",
        sa.Column("end_time", sa.Time(timezone=True), nullable=False),
    )
    op.drop_index(
        op.f("unique_active_booking"),
        table_name="bookings",
        postgresql_where="(status = 'ACTIVE'::statusbookingenum)",
    )
    op.create_index(
        "unique_active_booking",
        "bookings",
        ["room_id", "start_time", "booking_date"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )
    op.drop_constraint(
        op.f("bookings_slot_id_fkey"), "bookings", type_="foreignkey"
    )
    op.drop_column("bookings", "slot_id")


def downgrade() -> None:
    op.add_column(
        "bookings",
        sa.Column(
            "slot_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.create_foreign_key(
        op.f("bookings_slot_id_fkey"),
        "bookings",
        "timeslots",
        ["slot_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_index(
        "unique_active_booking",
        table_name="bookings",
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )
    op.create_index(
        op.f("unique_active_booking"),
        "bookings",
        ["room_id", "slot_id", "booking_date"],
        unique=True,
        postgresql_where="(status = 'ACTIVE'::statusbookingenum)",
    )
    op.drop_column("bookings", "end_time")
    op.drop_column("bookings", "start_time")
