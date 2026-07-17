from datetime import date
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query

from src.api.dependencies.db import DBDep
from src.schemas.bookings import AvailabilityResponse, BookingIn, BookingResponse, RoomAvailability
from src.services.bookings import BookingService
from src.utils.enums.status_bookings import StatusBookingEnum
from src.utils.exceptions.exceptions import BookingAlreadyBusyException, BookingNotFoundException, RoomNotFoundException
from src.utils.exceptions.http_exceptions import BookingAlreadyBusyHTTPException, BookingNotFoundHTTPException, RoomNotFoundHTTPException
from src.api.dependencies.users import get_employee_user, get_admin_user, EmployeeDep

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.get("/", status_code=200, response_model=list[BookingResponse], dependencies=[Depends(get_admin_user)])
async def get_all_bookings(db: DBDep,
                           date: date = Query(example="2026-07-16"),
                           status: StatusBookingEnum | None = Query(None),
                           room_id: int | None = Query(None)):
    return await BookingService(db).get_all_bookings_adm(room_id=room_id, booking_date=date, status=status)

@router.post("/{room_id}", status_code=201, response_model=BookingResponse)
async def create_booking(db: DBDep, room_id: Annotated[int, Path(ge=0)], user: EmployeeDep, booking_data: BookingIn):
    try:
        return await BookingService(db).create_booking(booking_data, user_id=user.id, room_id=room_id)
    except BookingAlreadyBusyException:
        raise BookingAlreadyBusyHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

@router.delete("/my/{booking_id}", status_code=200, response_model=BookingResponse)
async def cancelled_my_bookgng(db: DBDep, user: EmployeeDep, booking_id: Annotated[int, Path(ge=0)]):
    try:
        return await BookingService(db).soft_delete_booking(user_id=user.id, id=booking_id)
    except BookingNotFoundException:
        raise BookingNotFoundHTTPException

@router.delete("/{booking_id}", status_code=200, response_model=BookingResponse, dependencies=[Depends(get_admin_user)])
async def cancelled_user_booking(db: DBDep, booking_id: Annotated[int, Path(ge=0)]):
    try:
        return await BookingService(db).soft_delete_booking(id=booking_id)
    except BookingNotFoundException:
        raise BookingNotFoundHTTPException

@router.get("/my", status_code=200, response_model=list[BookingResponse])
async def get_my_bookings(db: DBDep, user: EmployeeDep):
    return await BookingService(db).get_my_bookings(user_id=user.id)

@router.get("/availability", status_code=200, response_model=AvailabilityResponse, dependencies=[Depends(get_employee_user)])
async def get_availability_by_date(db: DBDep, date: date = Query(example="2026-07-16")):
    return await BookingService(db).get_availability(booking_date=date)

@router.get("/availability/{room_id}", status_code=200, response_model=RoomAvailability, dependencies=[Depends(get_employee_user)])
async def get_availability_by_date_and_room(db: DBDep, room_id: int = Path(ge=0), date: date = Query(example="2026-07-16")):
    try:
        bookings = await BookingService(db).get_availability(booking_date=date, room_id=room_id)
        return bookings.rooms[0]
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
