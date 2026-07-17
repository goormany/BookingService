from datetime import date
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query

from src.api.dependencies.db import DBDep
from src.schemas.bookings import AvailabilityResponse, BookingIn, BookingResponse, RoomAvailability
from src.services.bookings import BookingService
from src.api.dependencies.paginations import PaginationDep
from src.utils.enums.status_bookings import StatusBookingEnum
from src.utils.exceptions.exceptions import BookingAlreadyBusyException, BookingNotFoundException, RoomNotFoundException
from src.utils.exceptions.http_exceptions import BookingAlreadyBusyHTTPException, BookingNotFoundHTTPException, RoomNotFoundHTTPException
from src.api.dependencies.users import get_employee_user, get_admin_user, EmployeeDep

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get(
    "/",
    status_code=200,
    response_model=list[BookingResponse],
    dependencies=[Depends(get_admin_user)],
    summary="Получить все бронирования (админ)",
    response_description="Список бронирований с фильтрацией и пагинацией",
)
async def get_all_bookings(db: DBDep,
                           pd: PaginationDep,
                           date: date = Query(example="2026-07-16"),
                           status: StatusBookingEnum | None = Query(None),
                           room_id: int | None = Query(None)):
    """
    Возвращает список всех бронирований с возможностью фильтрации.

    Параметры фильтрации:
    - **date**: Дата бронирования (обязательно, формат YYYY-MM-DD).
    - **status**: Статус бронирования (`active` / `cancelled`, необязательно).
    - **room_id**: ID комнаты (необязательно).

    Параметры пагинации:
    - **page**: Номер страницы (по умолч. 1).
    - **per_page**: Количество записей на странице (по умолч. 20, макс. 20).

    Доступ: admin.
    """
    return await BookingService(db).get_all_bookings_adm(
        per_page=pd.per_page, page=pd.page,
        room_id=room_id, booking_date=date, status=status)


@router.post(
    "/{room_id}",
    status_code=201,
    response_model=BookingResponse,
    summary="Создать бронирование",
    response_description="Данные созданного бронирования",
)
async def create_booking(db: DBDep, room_id: Annotated[int, Path(ge=0)], user: EmployeeDep, booking_data: BookingIn):
    """
    Создаёт бронирование комнаты на указанное время.

    - **room_id**: ID комнаты (>= 0).
    - **booking_date**: Дата бронирования (YYYY-MM-DD).
    - **start_time**: Время начала (HH:MM).
    - **end_time**: Время окончания (HH:MM).

    **Возможные ошибки:**
    - `409 Conflict` — комната уже забронирована на это время.
    - `404 Not Found` — комната с указанным ID не найдена.

    Доступ: employee, admin.
    """
    try:
        return await BookingService(db).create_booking(booking_data, user_id=user.id, room_id=room_id)
    except BookingAlreadyBusyException:
        raise BookingAlreadyBusyHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException


@router.delete(
    "/my/{booking_id}",
    status_code=200,
    response_model=BookingResponse,
    summary="Отменить своё бронирование",
    response_description="Данные отменённого бронирования",
)
async def cancelled_my_bookgng(db: DBDep, user: EmployeeDep, booking_id: Annotated[int, Path(ge=0)]):
    """
    Отменяет (мягко удаляет) собственное бронирование по его ID.

    - **booking_id**: ID бронирования (>= 0).

    **Возможные ошибки:**
    - `404 Not Found` — бронирование с указанным ID не найдено.

    Доступ: employee, admin.
    """
    try:
        return await BookingService(db).soft_delete_booking(user_id=user.id, id=booking_id)
    except BookingNotFoundException:
        raise BookingNotFoundHTTPException


@router.delete(
    "/{booking_id}",
    status_code=200,
    response_model=BookingResponse,
    dependencies=[Depends(get_admin_user)],
    summary="Отменить бронирование пользователя (админ)",
    response_description="Данные отменённого бронирования",
)
async def cancelled_user_booking(db: DBDep, booking_id: Annotated[int, Path(ge=0)]):
    """
    Отменяет (мягко удаляет) любое бронирование по его ID.

    - **booking_id**: ID бронирования (>= 0).

    **Возможные ошибки:**
    - `404 Not Found` — бронирование с указанным ID не найдено.

    Доступ: admin.
    """
    try:
        return await BookingService(db).soft_delete_booking(id=booking_id)
    except BookingNotFoundException:
        raise BookingNotFoundHTTPException


@router.get(
    "/my",
    status_code=200,
    response_model=list[BookingResponse],
    summary="Получить свои бронирования",
    response_description="Список бронирований текущего пользователя с пагинацией",
)
async def get_my_bookings(db: DBDep, user: EmployeeDep, pd: PaginationDep):
    """
    Возвращает список бронирований текущего пользователя с пагинацией.

    - **page**: Номер страницы (по умолч. 1).
    - **per_page**: Количество записей на странице (по умолч. 20, макс. 20).

    Доступ: employee, admin.
    """
    return await BookingService(db).get_my_bookings(per_page=pd.per_page, page=pd.page, user_id=user.id)


@router.get(
    "/availability",
    status_code=200,
    response_model=AvailabilityResponse,
    dependencies=[Depends(get_employee_user)],
    summary="Получить доступность комнат на дату",
    response_description="Список комнат со свободными временными интервалами",
)
async def get_availability_by_date(db: DBDep, pd: PaginationDep, date: date = Query(example="2026-07-16")):
    """
    Возвращает свободные временные интервалы для всех комнат на указанную дату.

    - **date**: Дата (YYYY-MM-DD, обязательна).
    - **page**: Номер страницы (по умолч. 1).
    - **per_page**: Количество записей на странице (по умолч. 20, макс. 20).

    Доступ: employee, admin.
    """
    return await BookingService(db).get_availability(booking_date=date,
                                                     per_page=pd.per_page,
                                                     page=pd.page)


@router.get(
    "/availability/{room_id}",
    status_code=200,
    response_model=RoomAvailability,
    dependencies=[Depends(get_employee_user)],
    summary="Получить доступность конкретной комнаты на дату",
    response_description="Свободные интервалы для указанной комнаты",
)
async def get_availability_by_date_and_room(db: DBDep, room_id: int = Path(ge=0), date: date = Query(example="2026-07-16")):
    """
    Возвращает свободные временные интервалы для конкретной комнаты на указанную дату.

    - **room_id**: ID комнаты (>= 0).
    - **date**: Дата (YYYY-MM-DD, обязательна).

    **Возможные ошибки:**
    - `404 Not Found` — комната с указанным ID не найдена.

    Доступ: employee, admin.
    """
    try:
        bookings = await BookingService(db).get_availability(booking_date=date, room_id=room_id)
        return bookings.rooms[0]
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException