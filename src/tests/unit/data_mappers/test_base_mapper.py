from datetime import date, datetime, time
from unittest.mock import MagicMock

from src.data_mappers.base import BaseDataMapper
from src.models.bookings import Bookings
from src.models.rooms import Rooms
from src.schemas.bookings import BookingResponse
from src.schemas.rooms import RoomCreate, RoomView
from src.utils.enums.status_bookings import StatusBookingEnum


class TestBaseDataMapper:
    def test_map_to_schema(self):
        mock_orm = MagicMock()
        mock_orm.id = 1
        mock_orm.user_id = 1
        mock_orm.room_id = 1
        mock_orm.booking_date = date(2026, 7, 18)
        mock_orm.start_time = time(10, 0)
        mock_orm.end_time = time(11, 0)
        mock_orm.status = StatusBookingEnum.ACTIVE
        mock_orm.created_at = datetime(2026, 7, 18, 10, 0, 0)

        class TestMapper(BaseDataMapper):
            db_model = Bookings
            schema = BookingResponse

        result = TestMapper.map_to_schema(mock_orm)
        assert isinstance(result, BookingResponse)
        assert result.id == 1

    def test_map_to_db_model(self):
        class TestMapper(BaseDataMapper):
            db_model = Rooms
            schema = RoomView

        schema = RoomCreate(name="room 1")
        result = TestMapper.map_to_db_model(schema)

        assert isinstance(result, Rooms)
        assert result.name == "room 1"
        assert result.description is None
