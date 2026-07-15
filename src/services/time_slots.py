from src.services.base import BaseServices
from src.schemas.time_slots import TimeSlotsIn, TimeSlotsResponse, TimeSlotsCreate
from src.utils.exceptions.exceptions import BookingRoomsInvalidObjReferences, BookingRoomsNotFoundObjException, BookingRoomsObjUniquessException, RoomNotFoundException, TimeSlotNotFoundException, TimeSlotsUniquessException

class TimeSlotService(BaseServices):
    async def create_slot(self, time_slots_data: TimeSlotsIn, room_id: int) -> TimeSlotsResponse:
        data = TimeSlotsCreate(**time_slots_data.model_dump(), room_id=room_id)
        try:
            slot = await self.db.time_slots.add(data)
        except BookingRoomsInvalidObjReferences:
            raise RoomNotFoundException
        except BookingRoomsObjUniquessException:
            raise TimeSlotsUniquessException
        await self.db.commit()
        return slot
    
    async def delete_slot(self, *args, **kwargs):
        try:
            slot = await self.db.time_slots.delete(*args, **kwargs)
        except BookingRoomsNotFoundObjException:
            raise TimeSlotNotFoundException
        await self.db.commit()
        return slot