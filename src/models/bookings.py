from datetime import date, time

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, ForeignKey, Index, Time

from src.db.database import Base
from src.utils.enums.status_bookings import StatusBookingEnum


class Bookings(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))

    start_time: Mapped[time] = mapped_column(Time(True))
    end_time: Mapped[time] = mapped_column(Time(True))

    booking_date: Mapped[date] = mapped_column(Date())
    status: Mapped[StatusBookingEnum] = mapped_column(
        default=StatusBookingEnum.ACTIVE.value
    )

    __table_args__ = (
        Index(
            "unique_active_booking",
            "room_id",
            "start_time",
            "booking_date",
            unique=True,
            postgresql_where=(status == StatusBookingEnum.ACTIVE.value),
        ),
    )
