from fastapi import APIRouter, Depends, Path

from src.api.dependencies.db import DBDep
from src.api.dependencies.paginations import PaginationDep
from src.schemas.rooms import RoomView, RoomWithSlotsResponse, RoomCreate, RoomUpdate
from src.services.rooms import RoomService
from src.utils.exceptions.exceptions import RoomNotFoundException, RoomUniquessException
from src.utils.exceptions.http_exceptions import RoomNotFoundHTTPException, RoomUniquessHTTPException
from src.api.dependencies.users import get_admin_user, get_employee_user

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("/", status_code=200, response_model=list[RoomView], dependencies=[Depends(get_employee_user)])
async def get_all_rooms(db: DBDep, pd: PaginationDep):
    return await RoomService(db).get_all(per_page=pd.per_page, page=pd.page)

@router.post("/", status_code=201, response_model=RoomView, dependencies=[Depends(get_admin_user)])
async def create_room(db: DBDep, room_data: RoomCreate):
    try:
        return await RoomService(db).create(room_data)
    except RoomUniquessException:
        raise RoomUniquessHTTPException
    
@router.get("/{room_id}", status_code=200, response_model=RoomWithSlotsResponse, dependencies=[Depends(get_employee_user)])
async def get_room_by_id(db: DBDep, room_id: int = Path(ge=0)):
    try:
        return await RoomService(db).get_room_with_slots(room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

@router.patch("/{room_id}", status_code=200, response_model=RoomView, dependencies=[Depends(get_admin_user)])
async def update_room_by_id(db: DBDep, room_data: RoomUpdate, room_id: int = Path(ge=0)):
    try:
        return await RoomService(db).update_room(room_data, id=room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except RoomUniquessException:
        raise RoomUniquessHTTPException

@router.delete("/{room_id}", status_code=200, response_model=RoomView, dependencies=[Depends(get_admin_user)])
async def delete_room_by_id(db: DBDep, room_id: int = Path(ge=0)):
    try:
        return await RoomService(db).delete_room(id=room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException