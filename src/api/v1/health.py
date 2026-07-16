from fastapi import APIRouter

from src.api.dependencies.db import DBDep
from src.services.health import HealthSearvice
from src.utils.exceptions.exceptions import BookingNotConnDBException
from src.utils.exceptions.http_exceptions import BookingNotConnDBHTTPException

router = APIRouter(prefix="/health", tags=["Health"])

@router.post("/", status_code=200)
async def check_health(db: DBDep):
    try:
        await HealthSearvice(db).check()
    except BookingNotConnDBException:
        raise BookingNotConnDBHTTPException
    return {"ok": True}