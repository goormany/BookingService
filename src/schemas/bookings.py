from datetime import date, datetime, time

from pydantic import BaseModel

from src.utils.enums.status_bookings import StatusBookingEnum

class BookingCreate(BaseModel):
    room_id: int
    slot_id: int
    booking_date: date

class BookingResponse(BookingCreate):
    id: int
    user_id: int
    username: str
    room_name: str
    start: time
    end: time
    status: StatusBookingEnum
    created_at: datetime

class SlotAvailability(BaseModel):
    slot_id: int
    start: time
    end: time
    is_available: bool

class RoomAvailability(BaseModel):
    room_id: int
    room_name: str
    slots: list[SlotAvailability]

class AvailabilityResponse(BaseModel):
    date: date
    rooms: list[RoomAvailability]