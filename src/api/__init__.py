from fastapi import APIRouter

from src.api.v1.router import router as v1_router

router = APIRouter(prefix="")
router.include_router(v1_router)

__all__ = ["router"]
