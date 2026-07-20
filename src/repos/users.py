from sqlalchemy import update
from sqlalchemy.exc import NoResultFound

from src.repos.base import BaseRepository
from src.data_mappers.users import UserDataMapper
from src.schemas.users import UserResponse, UserWithHashedPassword
from src.utils.exceptions.exceptions import UserNotFoundException


class UserRepository(BaseRepository):
    mapper = UserDataMapper

    async def get_user_with_hashed_password(
        self, *args, **kwargs
    ) -> UserWithHashedPassword:
        query = self._get_query_with_params(*args, **kwargs)
        result = await self.session.execute(query)

        try:
            return UserWithHashedPassword.model_validate(
                result.scalar_one(), from_attributes=True
            )
        except NoResultFound:
            raise UserNotFoundException

    async def soft_delete(self, user_id: int) -> UserResponse:
        stmt = (
            update(self.mapper.db_model)
            .filter_by(id=user_id)
            .values(is_active=False)
            .returning(self.mapper.db_model)
        )
        result = await self.session.execute(stmt)
        try:
            user = result.scalar_one()
        except NoResultFound:
            raise UserNotFoundException
        return self.mapper.map_to_schema(user)

    async def restore(self, user_id: int) -> UserResponse:
        stmt = (
            update(self.mapper.db_model)
            .filter_by(id=user_id)
            .values(is_active=True)
            .returning(self.mapper.db_model)
        )
        result = await self.session.execute(stmt)
        try:
            user = result.scalar_one()
        except NoResultFound:
            raise UserNotFoundException
        return self.mapper.map_to_schema(user)
