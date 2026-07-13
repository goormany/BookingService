from src.data_mappers.base import BaseDataMapper
from src.models.bookings import Bookings
from src.schemas.bookings import BookingResponse

class BookingDataMapper(BaseDataMapper):
    db_model = Bookings
    schema = BookingResponse