from datetime import time

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Time, ForeignKey, UniqueConstraint

from src.db.database import Base

class TimeSlots(Base):
    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE")
    )
    start: Mapped[time] = mapped_column(Time(True))
    end: Mapped[time] = mapped_column(Time(True))
    
    room: Mapped["Rooms"] = relationship(back_populates="slots") # type: ignore
    
    __table_args__ = (
        UniqueConstraint("room_id", "start", "end", name="uniqie_room_id_with_start_end_times"),
    )