from datetime import date

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, ForeignKey, Index

from src.db.database import Base
from src.utils.enums.status_bookings import StatusBookingEnum

class Bookings(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    slot_id: Mapped[int] = mapped_column(ForeignKey("timeslots.id", ondelete="CASCADE"))
    
    booking_date: Mapped[date] = mapped_column(Date())
    status: Mapped[StatusBookingEnum] = mapped_column(default=StatusBookingEnum.ACTIVE.value)
    
    __table_args__ = (
        Index(
            "unique_active_booking",
            "room_id", "slot_id", "booking_date",
            unique=True,
            postgresql_where=(status == StatusBookingEnum.ACTIVE.value)
        ),
    )