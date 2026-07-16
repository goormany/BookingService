from collections import defaultdict

from src.schemas.time_slots import TimeSlotsResponse
from src.services.base import BaseServices
from src.schemas.bookings import AvailabilityResponse, BookingCreate, BookingIn, BookingResponse, RoomAvailability, SoftDeleteBooking
from src.utils.enums.status_bookings import StatusBookingEnum
from src.utils.exceptions.exceptions import BookingAlreadyBusyException, BookingNotFoundException, BookingRoomsInvalidObjReferences, BookingRoomsNotFoundObjException, BookingRoomsObjUniquessException, RoomNotFoundException
from src.services.time_slots import TimeSlotService

class BookingService(BaseServices):    
    
    async def get_all_bookings_adm(self, *args, **kwargs) -> list[BookingResponse]:
        if kwargs.get("room_id", None) is None:
            kwargs.pop("room_id")
        if kwargs.get("status", None) is None:
            kwargs.pop("status")
        return await self.db.bookings.get_filtred(*args, **kwargs)
    
    async def create_booking(self, booking_data: BookingIn, room_id: int, user_id: int) -> BookingResponse:
        new_booking_data = BookingCreate(
            **booking_data.model_dump(),
            room_id=room_id,
            user_id=user_id
        )
        try:
            booking = await self.db.bookings.add(new_booking_data)
        except BookingRoomsObjUniquessException:
            raise BookingAlreadyBusyException
        except BookingRoomsInvalidObjReferences:
            raise RoomNotFoundException
        await self.db.commit()
        return booking
    
    async def get_my_bookings(self, user_id: int) -> list[BookingResponse]:
        return await self.db.bookings.get_filtred(user_id=user_id)
    
    async def soft_delete_booking(self, *args, **kwargs) -> BookingResponse:
        try:
            soft_delete_data = SoftDeleteBooking(status=StatusBookingEnum.CANCELLED)
            booking = await self.db.bookings.edit(soft_delete_data, True, *args, **kwargs)
        except BookingRoomsNotFoundObjException:
            raise BookingNotFoundException
        await self.db.commit()
        return booking