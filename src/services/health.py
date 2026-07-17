from src.services.base import BaseServices
from src.utils.exceptions.exceptions import BookingNotConnDBException, BookingNotConnRedisException

class HealthService(BaseServices):
    async def check(self) -> bool:
        try:
            await self.check_db()
        except BookingNotConnDBException:
            raise BookingNotConnDBException
    
    async def check_db(self) -> bool:
        try:
            return await self.db.health.check_connect_db()
        except BookingNotConnDBException:
            raise BookingNotConnDBException
    