from src.data_mappers.base import BaseDataMapper
from src.models.users import Users
from src.schemas.users import UserResponse

class RoomDataMapper(BaseDataMapper):
    db_model = Users
    schema = UserResponse