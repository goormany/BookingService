from datetime import date

from sqlalchemy import select

from src.schemas.bookings import BookingResponse
from src.repos.base import BaseRepository
from src.data_mappers.bookings import BookingDataMapper
from src.utils.enums.status_bookings import StatusBookingEnum


class BookingRepository(BaseRepository):
    mapper = BookingDataMapper

    async def get_active_bookings_by_date(self, booking_date: date) -> list[BookingResponse]:
        """Возвращает все активные бронирования на указанную дату"""
        query = (
            select(self.mapper.db_model)
            .filter_by(booking_date=booking_date, status=StatusBookingEnum.ACTIVE.value)
        )
        result = await self.session.execute(query)
        return [self.mapper.map_to_schema(booking) for booking in result.scalars().all()]
