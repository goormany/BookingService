from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from src.repos.base import BaseRepository
from src.data_mappers.rooms import RoomDataMapper
from src.schemas.rooms import RoomWithSlotsResponse
from src.utils.exceptions.exceptions import BookingRoomsNotFoundObjException, RoomNotFoundException


class RoomRepository(BaseRepository):
    mapper = RoomDataMapper

    async def get_room_with_slots(self, room_id: int) -> RoomWithSlotsResponse:
        query = (
            select(self.mapper.db_model)
            .where(self.mapper.db_model.id == room_id)
            .options(selectinload(self.mapper.db_model.slots))
        )
        result = await self.session.execute(query)
        try:
            room = result.scalar_one()
        except NoResultFound:
            raise RoomNotFoundException

        return RoomWithSlotsResponse.model_validate(room, from_attributes=True)