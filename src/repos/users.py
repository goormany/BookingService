from src.repos.base import BaseRepository
from src.data_mappers.users import UserDataMapper

class UserRepository(BaseRepository):
    mapper = UserDataMapper