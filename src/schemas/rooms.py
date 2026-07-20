from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.time_slots import TimeSlotsResponse
from src.schemas.validators import NonEmptyStr


class RoomBase(BaseModel):
    name: NonEmptyStr = Field(min_length=4)
    description: str | None = None


class RoomCreate(RoomBase):
    pass


class RoomView(RoomBase):
    id: int
    created_at: datetime


class RoomUpdate(RoomBase):
    name: NonEmptyStr | None = Field(None, min_length=4)
    description: str | None = None


class RoomWithSlotsResponse(RoomBase):
    id: int
    slots: list[TimeSlotsResponse]
