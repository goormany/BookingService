from sqlalchemy import select

from src.repos.base import BaseRepository
from src.utils.exceptions.exceptions import BookingNotConnDBException

class HealthRepository(BaseRepository):
    async def check_connect_db(self) -> bool:
        query = select(1)
        
        try:
            result = await self.session.execute(query)
            return result.scalar_one()
        except ConnectionRefusedError:
            raise BookingNotConnDBException
    