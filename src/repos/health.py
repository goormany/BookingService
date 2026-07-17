from sqlalchemy import select
from redis.exceptions import ConnectionError

from src.repos.base import BaseRepository
from src.utils.exceptions.exceptions import BookingNotConnDBException, BookingNotConnRedisException
from src.connectors.setup import redis_manager

class HealthRepository(BaseRepository):
    async def check_connect_db(self) -> bool:
        query = select(1)
        
        try:
            result = await self.session.execute(query)
            return result.scalar_one()
        except ConnectionRefusedError:
            raise BookingNotConnDBException
    
    async def check_connect_redis(self) -> bool:
        test_key = "test_key"
        test_value = "test_value"
        try:
            await redis_manager.set(test_key, test_value, 30)
            await redis_manager.get(test_key)
        except ConnectionError:
            raise BookingNotConnRedisException
        