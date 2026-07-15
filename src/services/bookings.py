from datetime import date

from src.services.base import BaseServices
from src.schemas.bookings import AvailabilityResponse, RoomAvailability, SlotAvailability


class BookingService(BaseServices):
    async def get_availability(self, booking_date: date) -> AvailabilityResponse:
        booked = await self.db.bookings.get_booked_slots_by_date(booking_date)
        booked_set = set(booked)

        rooms = await self.db.rooms.get_all_with_slots()

        rooms_availability: list[RoomAvailability] = []
        for room in rooms:
            slots_availability: list[SlotAvailability] = []
            for slot in room.slots:
                slots_availability.append(
                    SlotAvailability(
                        slot_id=slot.id,
                        start=slot.start,
                        end=slot.end,
                        is_available=(room.id, slot.id) not in booked_set,
                    )
                )
            rooms_availability.append(
                RoomAvailability(
                    room_id=room.id,
                    room_name=room.name,
                    slots=slots_availability,
                )
            )

        return AvailabilityResponse(
            date=booking_date,
            rooms=rooms_availability,
        )