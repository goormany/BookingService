from datetime import date

from fastapi import APIRouter, Query

from src.api.dependencies.db import DBDep
from src.schemas.bookings import AvailabilityResponse, BookingResponse
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/availability", status_code=200, response_model=AvailabilityResponse)
async def get_availability(db: DBDep, date: date = Query(..., description="Дата в формате YYYY-MM-DD")):
    return await BookingService(db).get_availability(date)
