from src.data_mappers.base import BaseDataMapper
from src.models.users import Users
from src.schemas.users import UserResponse

class UserDataMapper(BaseDataMapper):
    db_model = Users
    schema = UserResponse