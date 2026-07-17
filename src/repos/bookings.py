from datetime import date

from sqlalchemy import and_, exists, select

from src.schemas.bookings import BookingCreate, BookingResponse
from src.repos.base import BaseRepository
from src.data_mappers.bookings import BookingDataMapper
from src.utils.enums.status_bookings import StatusBookingEnum
from src.repos.time_slots import TimeSlotRepository
from src.utils.exceptions.exceptions import BookingAlreadyBusyException, BookingRoomsInvalidObjReferences, BookingRoomsObjUniquessException, RoomNotFoundException


class BookingRepository(BaseRepository):
    mapper = BookingDataMapper

    async def get_active_bookings_by_date(
        self, booking_date: date, room_id: int | None = None
    ) -> list[BookingResponse]:
        query = (
            select(self.mapper.db_model)
            .filter_by(booking_date=booking_date, status=StatusBookingEnum.ACTIVE.value)
        )
        if room_id is not None:
            query = query.filter_by(room_id=room_id)
        result = await self.session.execute(query)
        return [self.mapper.map_to_schema(booking) for booking in result.scalars().all()]

    async def create_booking(self, booking_data: BookingCreate) -> BookingResponse:
        model = self.mapper.db_model
        timeslots_model = TimeSlotRepository.mapper.db_model

        check = (
            select(
                exists(
                    select(1).where(
                        and_(
                            timeslots_model.room_id == booking_data.room_id,
                            timeslots_model.start <= booking_data.start_time,
                            timeslots_model.end >= booking_data.end_time,
                        )
                    )
                ).label("has_slot"),
                exists(
                    select(1).where(
                        and_(
                            model.status == StatusBookingEnum.ACTIVE.value,
                            model.room_id == booking_data.room_id,
                            model.booking_date == booking_data.booking_date,
                            model.start_time < booking_data.end_time,
                            model.end_time > booking_data.start_time,
                        )
                    )
                ).label("has_conflict"),
            )
        )
        result = await self.session.execute(check)
        row = result.one()
        if not row.has_slot:
            raise RoomNotFoundException
        if row.has_conflict:
            raise BookingAlreadyBusyException

        try:
            return await self.add(booking_data)
        except BookingRoomsObjUniquessException:
            raise BookingAlreadyBusyException
        except BookingRoomsInvalidObjReferences:
            raise RoomNotFoundException
