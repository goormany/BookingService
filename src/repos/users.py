from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.repos.base import BaseRepository
from src.data_mappers.users import UserDataMapper
from src.schemas.users import UserWithHashedPassword
from src.utils.exceptions.exceptions import UserNotFoundException

class UserRepository(BaseRepository):
    mapper = UserDataMapper
    
    async def get_user_with_hashed_password(self, *args, **kwargs) -> UserWithHashedPassword:
        query = self._get_query_with_params(*args, **kwargs)
        result = await self.session.execute(query)
        
        try:
            return UserWithHashedPassword.model_validate(result.scalar_one(), from_attributes=True)
        except NoResultFound:
            raise UserNotFoundException