from sqlalchemy import select

from src.repos.base import BaseRepository
from src.connectors.setup import redis_manager
from src.utils.enums.redis_state import RedisStateEnum
from src.utils.exceptions.exceptions import (
    BookingNotConnDBException,
    BookingNotConnRedisException,
)


class HealthRepository(BaseRepository):
    async def check_connect_db(self) -> bool:
        query = select(1)

        try:
            result = await self.session.execute(query)
            return result.scalar_one()
        except ConnectionRefusedError:
            raise BookingNotConnDBException

    async def check_connect_redis(self) -> bool:
        if redis_manager.state != RedisStateEnum.CONNECTED:
            raise BookingNotConnRedisException
        return True
