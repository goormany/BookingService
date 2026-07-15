from typing import Annotated

from fastapi import APIRouter, Path

from src.api.dependencies.db import DBDep
from src.schemas.time_slots import TimeSlotsIn, TimeSlotsResponse
from src.services.time_slots import TimeSlotService
from src.utils.exceptions.exceptions import RoomNotFoundException, TimeSlotNotFoundException, TimeSlotsUniquessException
from src.utils.exceptions.http_exceptions import RoomNotFoundHTTPException, TimeSlotNotFoundHTTPException, TimeSlotsUniquessHTTPException

router = APIRouter(prefix="/{room_id}/slots", tags=["Slots"])

@router.post("/", status_code=201, response_model=TimeSlotsResponse)
async def create_slots(db: DBDep, time_slots_data: TimeSlotsIn, room_id: int = Path(ge=0)):
    try:
        return await TimeSlotService(db).create_slot(time_slots_data, room_id=room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except TimeSlotsUniquessException:
        raise TimeSlotsUniquessHTTPException

@router.delete("/{slot_id}", status_code=200, response_model=TimeSlotsResponse)
async def delete_slot_by_id(db: DBDep, room_id: Annotated[int, Path(ge=0)], slot_id: Annotated[int, Path(ge=0)]):
    try:
        return await TimeSlotService(db).delete_slot(id=slot_id, room_id=room_id)
    except TimeSlotNotFoundException:
        raise TimeSlotNotFoundHTTPException