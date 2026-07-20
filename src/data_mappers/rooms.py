from src.data_mappers.base import BaseDataMapper
from src.models.rooms import Rooms
from src.schemas.rooms import RoomView


class RoomDataMapper(BaseDataMapper):
    db_model = Rooms
    schema = RoomView
