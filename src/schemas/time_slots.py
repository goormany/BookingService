from datetime import time

from pydantic import BaseModel


class TimeSlotsCreate(BaseModel):
    start: time
    end: time

class TimeSlotsResponse(TimeSlotsCreate):
    id: int
    room_id: int