from sqlalchemy.ext.asyncio import AsyncSession

from src.repos import (
    UserRepository,
    BookingRepository,
    TimeSlotRepository,
    RoomRepository,
    HealthRepository,
)


class DBManager:
    def __init__(self, session_maker):
        self.session_maker = session_maker

    async def __aenter__(self):
        self.session: AsyncSession = self.session_maker()

        # repos
        self.users = UserRepository(self.session)
        self.bookings = BookingRepository(self.session)
        self.time_slots = TimeSlotRepository(self.session)
        self.rooms = RoomRepository(self.session)
        self.health = HealthRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()
