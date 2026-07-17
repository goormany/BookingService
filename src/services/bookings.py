from datetime import date, time

from src.schemas.bookings import AvailabilityResponse, BookingCreate, BookingIn, BookingResponse, FreeInterval, RoomAvailability, SoftDeleteBooking
from src.services.base import BaseServices
from src.utils.enums.status_bookings import StatusBookingEnum
from src.utils.exceptions.exceptions import BookingAlreadyBusyException, BookingNotFoundException, BookingRoomsInvalidObjReferences, BookingRoomsNotFoundObjException, BookingRoomsObjUniquessException, RoomNotFoundException, TimeValueValidationException

class BookingService(BaseServices):
    def _compute_free_slots(
        self,
        slots: list,
        booked_intervals: list[tuple[time, time]],
    ) -> list[FreeInterval]:
        free_slots: list[FreeInterval] = []
        for slot in slots:
            start = slot.start
            end = slot.end
            
            overlapping = [
                (bs, be) for bs, be in booked_intervals
                if bs < end and be > start
            ]
            overlapping.sort(key=lambda x: x[0])
            
            cursor = start
            for bs, be in overlapping:
                if cursor < bs:
                    free_slots.append(FreeInterval(start_time=cursor, end_time=bs))
                cursor = max(cursor, be)
            
            if cursor < end:
                free_slots.append(FreeInterval(start_time=cursor, end_time=end))
        
        return free_slots
    
    async def get_availability(
        self,
        booking_date: date,
        per_page: int | None = None,
        page: int | None = None,
        room_id: int | None = None
    ) -> AvailabilityResponse:
        if room_id is not None:
            try:
                rooms = [await self.db.rooms.get_room_with_slots(room_id)]
            except RoomNotFoundException:
                raise RoomNotFoundException
        else:
            rooms = await self.db.rooms.get_all_with_slots(per_page=per_page, page=page)
        
        bookings = await self.db.bookings.get_active_bookings_by_date(
            booking_date, room_id=room_id
        )
        
        # Группируем бронирования по комнатам
        bookings_by_room: dict[int, list[tuple[time, time]]] = {}
        for booking in bookings:
            bookings_by_room.setdefault(booking.room_id, []).append(
                (booking.start_time, booking.end_time)
            )
        
        room_availabilities: list[RoomAvailability] = []
        
        for room in rooms:
            room_booked = bookings_by_room.get(room.id, [])
            free_slots = self._compute_free_slots(room.slots, room_booked)
            
            room_availabilities.append(RoomAvailability(
                room_id=room.id,
                room_name=room.name,
                slots=free_slots,
            ))
        
        return AvailabilityResponse(date=booking_date, rooms=room_availabilities)
    
    async def get_all_bookings_adm(self, per_page: int, page: int, *args, **kwargs) -> list[BookingResponse]:
        if kwargs.get("room_id", None) is None:
            kwargs.pop("room_id")
        if kwargs.get("status", None) is None:
            kwargs.pop("status")
        return await self.db.bookings.get_filtred(per_page=per_page, page=page, *args, **kwargs)
    
    async def create_booking(self, booking_data: BookingIn, room_id: int, user_id: int) -> BookingResponse:
        try:
            new_booking_data = BookingCreate(
                **booking_data.model_dump(),
                room_id=room_id,
                user_id=user_id
            )
        except TimeValueValidationException:
            raise TimeValueValidationException
        try:
            booking = await self.db.bookings.create_booking(new_booking_data)
        except BookingAlreadyBusyException:
            raise BookingAlreadyBusyException
        except RoomNotFoundException:
            raise RoomNotFoundException
        await self.db.commit()
        return booking
    
    async def get_my_bookings(self, per_page: int, page: int, user_id: int) -> list[BookingResponse]:
        return await self.db.bookings.get_filtred(per_page=per_page, page=page, user_id=user_id)
    
    async def soft_delete_booking(self, *args, **kwargs) -> BookingResponse:
        try:
            soft_delete_data = SoftDeleteBooking(status=StatusBookingEnum.CANCELLED)
            booking = await self.db.bookings.edit(soft_delete_data, True, *args, **kwargs)
        except BookingRoomsNotFoundObjException:
            raise BookingNotFoundException
        await self.db.commit()
        return booking