from fastapi import APIRouter

from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as user_router
from src.api.v1.rooms import router as room_router
from src.api.v1.time_slots import router as time_slots_router

router = APIRouter(prefix="/v1")

room_router.include_router(time_slots_router)

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(room_router)