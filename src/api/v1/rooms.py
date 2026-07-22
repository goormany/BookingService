from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from src.api.dependencies.db import DBDep
from src.api.dependencies.paginations import PaginationDep
from src.schemas.bookings import BookingResponse
from src.schemas.rooms import RoomView, RoomWithSlotsResponse, RoomCreate, RoomUpdate
from src.services.bookings import BookingService
from src.services.rooms import RoomService
from src.utils.enums.cache_ns import CacheNSEnum
from src.utils.exceptions.exceptions import RoomNotFoundException, RoomUniquessException
from src.utils.exceptions.http_exceptions import (
    RoomNotFoundHTTPException,
    RoomUniquessHTTPException,
)
from src.api.dependencies.users import get_admin_user, get_employee_user

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get(
    "/",
    status_code=200,
    response_model=list[RoomView],
    dependencies=[Depends(get_employee_user)],
    summary="Получить список всех комнат",
    response_description="Список комнат с пагинацией",
)
@cache(expire=3600, namespace=CacheNSEnum.ALL_ROOMS.value)
async def get_all_rooms(db: DBDep, pd: PaginationDep):
    """
    Возвращает список всех переговорных комнат с пагинацией.

    Параметры пагинации:
    - **page**: Номер страницы (по умолч. 1).
    - **per_page**: Количество записей на странице (по умолч. 20, макс. 20).

    Доступ: employee, admin.
    """
    return await RoomService(db).get_all(per_page=pd.per_page, page=pd.page)


@router.post(
    "/",
    status_code=201,
    response_model=RoomView,
    dependencies=[Depends(get_admin_user)],
    summary="Создать новую комнату",
    response_description="Данные созданной комнаты",
)
async def create_room(db: DBDep, room_data: RoomCreate):
    """
    Создаёт новую переговорную комнату.

    - **name**: Название комнаты.
    - **description**: Описание комнаты (необязательно).

    **Возможные ошибки:**
    - `409 Conflict` - Ошибка уникальности комнаты.

    Доступ: admin.
    """
    try:
        room = await RoomService(db).create(room_data)
        await FastAPICache.clear(namespace=CacheNSEnum.ALL_ROOMS.value)
        return room
    except RoomUniquessException:
        raise RoomUniquessHTTPException


@router.get(
    "/{room_id}",
    status_code=200,
    response_model=RoomWithSlotsResponse,
    dependencies=[Depends(get_employee_user)],
    summary="Получить комнату по ID",
    response_description="Данные комнаты со списком временных слотов",
)
async def get_room_by_id(db: DBDep, room_id: int = Path(ge=0)):
    """
    Возвращает комнату по её ID вместе со списком временных слотов.

    - **room_id**: ID комнаты (>= 0).

    **Возможные ошибки:**
    - `404 Not Found` - комната с указанным ID не найдена.

    Доступ: employee, admin.
    """
    try:
        return await RoomService(db).get_room_with_slots(room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException


@router.patch(
    "/{room_id}",
    status_code=200,
    response_model=RoomView,
    dependencies=[Depends(get_admin_user)],
    summary="Обновить данные комнаты",
    response_description="Обновлённые данные комнаты",
)
async def update_room_by_id(
    db: DBDep, room_data: RoomUpdate, room_id: int = Path(ge=0)
):
    """
    Частично обновляет данные комнаты.

    - **room_id**: ID комнаты (>= 0).
    - **name**: Новое название (необязательно).
    - **description**: Новое описание (необязательно).

    **Возможные ошибки:**
    - `404 Not Found` - комната с указанным ID не найдена.
    - `409 Conflict` - комната с таким названием уже существует.

    Доступ: admin.
    """
    try:
        room = await RoomService(db).update_room(room_data, id=room_id)
        await FastAPICache.clear(namespace=CacheNSEnum.ALL_ROOMS.value)
        return room
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except RoomUniquessException:
        raise RoomUniquessHTTPException


@router.delete(
    "/{room_id}",
    status_code=200,
    response_model=RoomView,
    dependencies=[Depends(get_admin_user)],
    summary="Удалить комнату",
    response_description="Данные удалённой комнаты",
)
async def delete_room_by_id(db: DBDep, room_id: int = Path(ge=0)):
    """
    Удаляет комнату по её ID.

    - **room_id**: ID комнаты (>= 0).

    **Возможные ошибки:**
    - `404 Not Found` - комната с указанным ID не найдена.

    Доступ: admin.
    """
    try:
        room = await RoomService(db).delete_room(id=room_id)
        await FastAPICache.clear(namespace=CacheNSEnum.ALL_ROOMS.value)
        await FastAPICache.clear(namespace=CacheNSEnum.AVAILABILITY.value)
        await FastAPICache.clear(namespace=CacheNSEnum.BOOKINGS_BY_ROOM_ID.value)
        await FastAPICache.clear(namespace=CacheNSEnum.ALL_BOOKINGS.value)
        return room
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException


@router.get(
    "/{room_id}/bookings",
    status_code=200,
    response_model=list[BookingResponse],
    summary="Получить бронирования комнаты",
    response_description="Список бронирований для указанной комнаты",
    dependencies=[Depends(get_admin_user)],
)
@cache(expire=3600, namespace=CacheNSEnum.BOOKINGS_BY_ROOM_ID.value)
async def get_bookings_by_room(
    db: DBDep,
    room_id: Annotated[int, Path(ge=0)],
    pd: PaginationDep,
):
    """
    Возвращает список бронирований для комнаты с пагинацией.

    - **room_id**: ID комнаты (>= 0).
    - **page**: Номер страницы (по умолч. 1).
    - **per_page**: Количество записей на странице (по умолч. 20, макс. 20).

    Доступ: admin.
    """
    return await BookingService(db).get_bookings_by_room(
        room_id=room_id,
        per_page=pd.per_page,
        page=pd.page,
    )
