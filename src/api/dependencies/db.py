from typing import Annotated

from fastapi import Depends

from src.db.db_manager import DBManager
from src.db.database import session_maker


async def get_db():
    async with DBManager(session_maker) as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
