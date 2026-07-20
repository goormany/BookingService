from datetime import datetime, time

from pydantic import BaseModel, Field, field_validator, model_validator

from src.schemas.validators import validate_and_convert_time
from src.utils.exceptions.exceptions import TimeValueValidationException


class TimeSlotsIn(BaseModel):
    start: str = Field(examples=["06:00"])
    end: str = Field(examples=["15:00"])

    @field_validator("start", "end")
    @classmethod
    def validate_time(cls, v: str) -> time:
        return validate_and_convert_time(v)


class TimeSlotsCreate(BaseModel):
    start: time
    end: time
    room_id: int

    @model_validator(mode="after")
    def check_times(self):
        if self.start >= self.end:
            raise TimeValueValidationException
        return self


class TimeSlotsResponse(TimeSlotsCreate):
    id: int
    created_at: datetime
