from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.repos.base import BaseRepository
from src.data_mappers.rooms import RoomDataMapper
from src.schemas.rooms import RoomWithSlotsResponse


class RoomRepository(BaseRepository):
    mapper = RoomDataMapper

    async def get_room_with_slots(self, room_id: int) -> RoomWithSlotsResponse:
        query = (
            select(self.mapper.db_model)
            .where(self.mapper.db_model.id == room_id)
            .options(selectinload(self.mapper.db_model.slots))
        )
        result = await self.session.execute(query)
        row = result.scalar_one_or_none()

        if row is None:
            from src.utils.exceptions.exceptions import BookingRoomsNotFoundObjException
            raise BookingRoomsNotFoundObjException

        return RoomWithSlotsResponse.model_validate(row, from_attributes=True)

    async def get_all_with_slots(self) -> list[RoomWithSlotsResponse]:
        query = (
            select(self.mapper.db_model)
            .options(selectinload(self.mapper.db_model.slots))
        )
        result = await self.session.execute(query)
        rooms = result.scalars().all()
        return [RoomWithSlotsResponse.model_validate(room, from_attributes=True) for room in rooms]