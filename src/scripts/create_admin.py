import asyncio
from getpass import getpass

from src.db.database import session_maker_null_pool
from src.db.db_manager import DBManager
from src.schemas.users import UserCreate, UserIn
from src.services.auth import AuthServices
from src.utils.enums.user_roles import UserRoleEnum


async def create_admin():
    username = input("enter username: ")
    password = getpass("enter password: ")
    
    user_in = UserIn(
        username=username,
        password=password
    )
    user_data = UserCreate(
        username=user_in.username,
        hashed_password=AuthServices.get_password_hash(user_in.password),
        role=UserRoleEnum.ADMIN
    )
    async with DBManager(session_maker_null_pool) as db:
        await db.users.add(user_data)
        await db.commit()
    
    print("admin created")
    
if __name__ == "__main__":
    asyncio.run(create_admin())