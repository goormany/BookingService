from src.data_mappers.bookings import BookingDataMapper
from src.data_mappers.rooms import RoomDataMapper
from src.data_mappers.time_slots import TimeSlotsDataMapper
from src.data_mappers.users import UserDataMapper
from src.models.bookings import Bookings
from src.models.rooms import Rooms
from src.models.time_slots import TimeSlots
from src.models.users import Users
from src.schemas.bookings import BookingResponse
from src.schemas.rooms import RoomView
from src.schemas.time_slots import TimeSlotsResponse
from src.schemas.users import UserResponse


class TestDataMapper:
    def test_booking_mapper_attr(self):
        assert BookingDataMapper.db_model == Bookings
        assert BookingDataMapper.schema == BookingResponse

    def test_rooms_mapper_attr(self):
        assert RoomDataMapper.db_model == Rooms
        assert RoomDataMapper.schema == RoomView

    def test_user_mapper_attr(self):
        assert UserDataMapper.db_model == Users
        assert UserDataMapper.schema == UserResponse

    def test_time_slots_mapper_attr(self):
        assert TimeSlotsDataMapper.db_model == TimeSlots
        assert TimeSlotsDataMapper.schema == TimeSlotsResponse