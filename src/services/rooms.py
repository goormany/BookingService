from src.services.base import BaseServices
from src.schemas.rooms import RoomCreate, RoomUpdate, RoomView
from src.utils.exceptions.exceptions import BookingRoomsNotFoundObjException, BookingRoomsObjUniquessException, RoomNotFoundException, RoomUniquessException

class RoomService(BaseServices):
    async def get_all(self, per_page: int, page: int) -> list[RoomView]:
        return await self.db.rooms.get_all(per_page=per_page, page=page)
    
    async def create(self, room_data: RoomCreate) -> RoomView:
        try:
            room = await self.db.rooms.add(room_data)
        except BookingRoomsObjUniquessException:
            raise RoomUniquessException
        await self.db.commit()
        
        return room
    
    async def get_room(self, *args, **kwargs) -> RoomView:
        try:
            return await self.db.rooms.get_one(*args, **kwargs)
        except BookingRoomsNotFoundObjException:
            raise RoomNotFoundException
        
    async def get_room_with_slots(self, room_id: int):
        try:
            return await self.db.rooms.get_room_with_slots(room_id)
        except RoomNotFoundException:
            raise RoomNotFoundException
        
    async def update_room(self, room_data: RoomUpdate, *args, **kwargs):
        try:
            room = await self.db.rooms.edit(room_data, True, *args, **kwargs)
        except BookingRoomsNotFoundObjException:
            raise RoomNotFoundException
        except BookingRoomsObjUniquessException:
            raise RoomUniquessException
        await self.db.commit()
        return room
    
    async def delete_room(self, *args, **kwargs):
        try:
            room = await self.db.rooms.delete(*args, **kwargs)
        except BookingRoomsNotFoundObjException:
            raise RoomNotFoundException
        await self.db.commit()
        return room