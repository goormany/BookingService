from typing import Annotated

from fastapi import APIRouter, Depends, Path

from src.api.dependencies.db import DBDep
from src.schemas.time_slots import TimeSlotsIn, TimeSlotsResponse
from src.services.time_slots import TimeSlotService
from src.utils.exceptions.exceptions import RoomNotFoundException, TimeSlotNotFoundException, TimeSlotValidationError, TimeSlotsUniquessException
from src.utils.exceptions.http_exceptions import RoomNotFoundHTTPException, TimeSlotNotFoundHTTPException, TimeSlotValidationHTTPException, TimeSlotsUniquessHTTPException
from src.api.dependencies.users import get_admin_user

router = APIRouter(prefix="/{room_id}/slots", tags=["Slots"], dependencies=[Depends(get_admin_user)])


@router.post(
    "/",
    status_code=201,
    response_model=TimeSlotsResponse,
    summary="Создать временной слот для комнаты",
    response_description="Данные созданного временного слота",
)
async def create_slots(db: DBDep, time_slots_data: TimeSlotsIn, room_id: int = Path(ge=0)):
    """
    Создаёт временной слот (расписание) для указанной комнаты.

    - **room_id**: ID комнаты (>= 0).
    - **start**: Время начала (HH:MM).
    - **end**: Время окончания (HH:MM).

    **Возможные ошибки:**
    - `404 Not Found` — комната с указанным ID не найдена.
    - `409 Conflict` — для этой комнаты уже есть слот на это время или не верные данные времени для слота.

    Доступ: admin.
    """
    try:
        return await TimeSlotService(db).create_slot(time_slots_data, room_id=room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except TimeSlotsUniquessException:
        raise TimeSlotsUniquessHTTPException
    except TimeSlotValidationError:
        raise TimeSlotValidationHTTPException


@router.delete(
    "/{slot_id}",
    status_code=200,
    response_model=TimeSlotsResponse,
    summary="Удалить временной слот",
    response_description="Данные удалённого временного слота",
)
async def delete_slot_by_id(db: DBDep, room_id: Annotated[int, Path(ge=0)], slot_id: Annotated[int, Path(ge=0)]):
    """
    Удаляет временной слот по его ID.

    - **room_id**: ID комнаты (>= 0).
    - **slot_id**: ID временного слота (>= 0).

    **Возможные ошибки:**
    - `404 Not Found` — временной слот с указанным ID не найден.

    Доступ: admin.
    """
    try:
        return await TimeSlotService(db).delete_slot(id=slot_id, room_id=room_id)
    except TimeSlotNotFoundException:
        raise TimeSlotNotFoundHTTPException