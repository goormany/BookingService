from datetime import date

from sqlalchemy import select

from src.models.bookings import Bookings
from src.repos.base import BaseRepository
from src.data_mappers.bookings import BookingDataMapper
from src.utils.enums.status_bookings import StatusBookingEnum


class BookingRepository(BaseRepository):
    mapper = BookingDataMapper

    async def get_booked_slots_by_date(self, booking_date: date) -> list[tuple[int, int]]:
        query = (
            select(Bookings.room_id, Bookings.slot_id)
            .where(Bookings.booking_date == booking_date)
            .where(Bookings.status == StatusBookingEnum.ACTIVE.value)
        )
        result = await self.session.execute(query)
        return result.all()  # [(room_id, slot_id)]
