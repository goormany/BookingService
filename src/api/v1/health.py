from fastapi import APIRouter

from src.api.dependencies.db import DBDep
from src.services.health import HealthService
from src.utils.exceptions.exceptions import BookingNotConnDBException, BookingNotConnRedisException
from src.utils.exceptions.http_exceptions import BookingNotConnDBHTTPException, BookingNotConnRedisHTTPException

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
    - `500 Internal Server Error` — нет подключения к базе данных или redis.
    """
    try:
        await HealthService(db).check()
    except BookingNotConnDBException:
        raise BookingNotConnDBHTTPException
    except BookingNotConnRedisException:
        raise BookingNotConnRedisHTTPException
    return {"ok": True}
