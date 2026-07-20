from datetime import date, datetime, time

from pydantic import BaseModel, Field, field_validator, model_validator

from src.schemas.validators import (
    validate_and_convert_time,
    validate_booking_date_not_in_past,
)
from src.utils.enums.status_bookings import StatusBookingEnum
from src.utils.exceptions.exceptions import TimeValueValidationException


class BookingIn(BaseModel):
    booking_date: date
    start_time: str = Field(examples=["06:00"])
    end_time: str = Field(examples=["12:00"])

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time(cls, v: str) -> time:
        return validate_and_convert_time(v)

    @field_validator("booking_date")
    @classmethod
    def validate_date_not_in_past(cls, v: date) -> date:
        return validate_booking_date_not_in_past(v)


class FreeInterval(BaseModel):
    start_time: time
    end_time: time


class BookingCreate(FreeInterval):
    booking_date: date
    user_id: int
    room_id: int

    @model_validator(mode="after")
    def check_time(self):
        if self.start_time >= self.end_time:
            raise TimeValueValidationException
        return self


class BookingResponse(BookingCreate):
    id: int
    created_at: datetime
    status: StatusBookingEnum


class RoomAvailability(BaseModel):
    room_id: int
    room_name: str
    slots: list[FreeInterval]


class AvailabilityResponse(BaseModel):
    date: date
    rooms: list[RoomAvailability]


class SoftDeleteBooking(BaseModel):
    status: StatusBookingEnum = StatusBookingEnum.CANCELLED
