from datetime import datetime, time, timezone
import re

from pydantic import BaseModel, Field, field_validator


class TimeSlotsIn(BaseModel):
    start: str = Field(examples=["06:00"])
    end: str = Field(examples=["15:00"])
    
    @field_validator('start', 'end')
    @classmethod
    def validate_and_convert_time(cls, v: str) -> str:
        if not re.match(r'^\d{2}:\d{2}$', v):
            raise ValueError(f'Время должно быть в формате HH:MM, получено {v}')
        
        hours, minutes = map(int, v.split(':'))
        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
            raise ValueError(f'Неверное время: {v}')
        
        return time(hours, minutes, tzinfo=timezone.utc)

class TimeSlotsCreate(BaseModel):
    start: time
    end: time
    room_id: int

class TimeSlotsResponse(TimeSlotsCreate):
    id: int
    created_at: datetime