from fastapi import APIRouter

from src.schemas.users import UserResponse
from src.api.dependencies.db import DBDep
from src.api.dependencies.users import CurUserDep

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse, status_code=200)
async def get_user_me(user_data: CurUserDep):
    return user_data