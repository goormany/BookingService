from src.repos.base import BaseRepository
from src.data_mappers.rooms import RoomDataMapper


class RoomRepository(BaseRepository):
    mapper = RoomDataMapper