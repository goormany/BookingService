from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from src.db.database import Base

class Rooms(Base):
    name: Mapped[str] = mapped_column(String(64), index=True)
    description: Mapped[str]
    
    slots: Mapped["TimeSlots"] = relationship(back_populates="slots") # type: ignore