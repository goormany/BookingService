from src.repos.base import BaseRepository
from src.data_mappers.bookings import BookingDataMapper

class BookingRepository(BaseRepository):
    mapper = BookingDataMapper