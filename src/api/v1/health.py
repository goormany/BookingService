from fastapi import APIRouter

from src.api.dependencies.db import DBDep
from src.services.health import HealthSearvice
from src.utils.exceptions.exceptions import BookingNotConnDBException
from src.utils.exceptions.http_exceptions import BookingNotConnDBHTTPException

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "/",
    status_code=200,
    summary="Проверка состояния сервиса",
    response_description="Статус подключения к базе данных",
)
async def check_health(db: DBDep):
    """
    Проверяет работоспособность сервиса и подключение к базе данных.

    **Возможные ошибки:**
    - `500 Internal Server Error` — нет подключения к базе данных.
    """
    try:
        await HealthSearvice(db).check()
    except BookingNotConnDBException:
        raise BookingNotConnDBHTTPException
    return {"ok": True}