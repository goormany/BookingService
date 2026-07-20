import pytest
from httpx import AsyncClient, ASGITransport

from src.api.dependencies.db import get_db
from src.config import settings
from src.db.database import engine_null_pool, Base, session_maker_null_pool
from src.db.db_manager import DBManager
from src.main import app
from src.schemas.users import UserCreate
from src.services.auth import AuthServices
from src.utils.enums.user_roles import UserRoleEnum


@pytest.fixture(scope="session", autouse=True)
async def check_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def init_db(check_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db_null_pool():
    async with DBManager(session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> DBManager:  # type: ignore
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session", autouse=True)
async def create_admin_user(init_db):
    async for db in get_db_null_pool():
        hashed_password = AuthServices.get_password_hash("admin")
        user_data = UserCreate(
            username="admin", hashed_password=hashed_password, role=UserRoleEnum.ADMIN
        )
        await db.users.add(user_data)
        await db.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncClient:  # type: ignore
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(ac):
    await ac.post(
        "/api/v1/auth/register", json={"username": "employee", "password": "employee"}
    )


@pytest.fixture(scope="session")
async def employee_ac():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/api/v1/auth/login", data={"username": "employee", "password": "employee"}
        )
        ac.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
        yield ac


@pytest.fixture(scope="session")
async def admin_ac(create_admin_user):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/api/v1/auth/login", data={"username": "admin", "password": "admin"}
        )
        ac.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
        yield ac
