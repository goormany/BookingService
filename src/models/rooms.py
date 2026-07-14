from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from src.db.database import Base

class Rooms(Base):
    name: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str] = mapped_column(nullable=True)
    
    slots: Mapped[list["TimeSlots"]] = relationship(back_populates="room") # type: ignore