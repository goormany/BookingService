from sqlalchemy import select
from redis.exceptions import TimeoutError as RedisTimeoutError

from src.repos.base import BaseRepository
from src.connectors.setup import redis_manager
from src.utils.exceptions.exceptions import BookingNotConnDBException, BookingNotConnRedisException


class HealthRepository(BaseRepository):
    async def check_connect_db(self) -> bool:
        query = select(1)

        try:
            result = await self.session.execute(query)
            return result.scalar_one()
        except ConnectionRefusedError:
            raise BookingNotConnDBException
    
    async def check_connect_redis(self) -> bool:
        key = "test_key"
        value = "test_value"
        try:
            await redis_manager.set(key, value, expire=60)
            value  = await redis_manager.get(key)
        except RedisTimeoutError:
            raise BookingNotConnRedisException
