from datetime import datetime

from pydantic import BaseModel

from src.schemas.time_slots import TimeSlotsResponse

class RoomCreate(BaseModel):
    name: str
    description: str | None = None
    
class RoomView(RoomCreate):
    id: int
    created_ad: datetime

class RoomUpdate(RoomCreate):
    name: str | None = None
    
class RoomWithSlotsResponse(RoomCreate):
    id: int
    slots: list[TimeSlotsResponse]
    