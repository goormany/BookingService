from fastapi import APIRouter, Path

from src.api.dependencies.db import DBDep
from src.schemas.rooms import RoomView, RoomCreate, RoomUpdate
from src.services.rooms import RoomService
from src.utils.exceptions.exceptions import RoomNotFoundException, RoomUniquessException
from src.utils.exceptions.http_exceptions import RoomNotFoundHTTPException, RoomUniquessHTTPException

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("/", status_code=200, response_model=list[RoomView])
async def get_all_rooms(db: DBDep):
    return await RoomService(db).get_all()

@router.post("/", status_code=201, response_model=RoomView)
async def create_room(db: DBDep, room_data: RoomCreate):
    try:
        return await RoomService(db).create(room_data)
    except RoomUniquessException:
        raise RoomUniquessHTTPException
    
@router.get("/{room_id}", status_code=200, response_model=RoomView)
async def get_room_by_id(db: DBDep, room_id: int = Path(ge=0)):
    try:
        return await RoomService(db).get_room(id=room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

@router.patch("/{room_id}", status_code=200, response_model=RoomView)
async def update_room_by_id(db: DBDep, room_data: RoomUpdate, room_id: int = Path(ge=0)):
    try:
        return await RoomService(db).update_room(room_data, id=room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except RoomUniquessException:
        raise RoomUniquessHTTPException

@router.delete("/{room_id}", status_code=200, response_model=RoomView)
async def delete_room_by_id(db: DBDep, room_id: int = Path(ge=0)):
    try:
        return await RoomService(db).delete_room(id=room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException