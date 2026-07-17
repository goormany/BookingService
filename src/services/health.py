from src.services.base import BaseServices
from src.utils.exceptions.exceptions import BookingNotConnDBException

class HealthService(BaseServices):
    async def check(self) -> bool:
        try:
            return await self.db.health.check_connect_db()
        except BookingNotConnDBException:
            raise BookingNotConnDBException