from sqlalchemy.ext.asyncio import AsyncSession


class DBManager:
    def __init__(self, session_maker):
        self.session_maker = session_maker
    
    async def __aenter__(self):
        self.session: AsyncSession = self.session_maker()
        
        # repos
        
        
        return self
    
    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()