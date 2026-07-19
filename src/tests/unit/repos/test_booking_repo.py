from datetime import date, time
from unittest.mock import AsyncMock, MagicMock, create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repos.bookings import BookingRepository
from src.data_mappers.bookings import BookingDataMapper
from src.models.bookings import Bookings
from src.schemas.bookings import BookingCreate
from src.utils.enums.status_bookings import StatusBookingEnum
from src.utils.exceptions.exceptions import BookingAlreadyBusyException, BookingRoomsInvalidObjReferences, BookingRoomsObjUniquessException, RoomNotFoundException

class TestBookingDataMapper(BookingDataMapper):
    @classmethod
    def map_to_schema(cls, obj):
        return f"map_{obj.id}"

@pytest.fixture
def repo(mock_session):
    repo = BookingRepository(mock_session)
    repo.mapper = TestBookingDataMapper
    return repo

@pytest.fixture
def mock_model():
    return Bookings(
        id=1,
        user_id=1,
        room_id=1,
        start_time=time(12, 0),
        end_time=time(15, 0),
        booking_date=date(2026, 7, 19),
        status=StatusBookingEnum.ACTIVE.value
    )

@pytest.fixture()
def mock_create_booking_schema():
    return BookingCreate(
        start_time=time(12, 0),
        end_time=time(15, 0),
        booking_date=date(2026, 7, 19),
        user_id=1,
        room_id=1
    )

class TestGetActiveBookingsByDate:
    async def test_get_active_bookings_by_date_success_without_room_id(self, repo, mock_session, mock_model):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_model]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_active_bookings_by_date(date(2026, 7, 19))
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        result = result[0]
        assert isinstance(result, str)
        assert result == "map_1"
        mock_session.execute.assert_called_once()
    
    async def test_get_active_bookings_by_date_success_with_room_id(self, repo, mock_session, mock_model):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_model]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_active_bookings_by_date(date(2026, 7, 19), room_id=5)
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        result = result[0]
        assert isinstance(result, str)
        assert result == "map_1"
        mock_session.execute.assert_called_once()

    async def test_get_active_bookings_by_date_success_not_found_booking(self, repo, mock_session):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_active_bookings_by_date(date(1970, 7, 19), room_id=1000)
        
        assert isinstance(result, list)
        assert len(result) == 0
        mock_session.execute.assert_called_once()

class TestCreateBooking:
    @pytest.fixture
    def repo_with_mock_add(self, repo):
        repo.add = AsyncMock(return_value=True)
        return repo
    
    async def test_create_booking_success(self, repo, mock_model, mock_session, mock_create_booking_schema):
        mock_row = MagicMock()
        mock_row.has_slot = True
        mock_row.has_conflict = False
        
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_session.execute.return_value = mock_result
        
        repo.add = AsyncMock(return_value=mock_model)
        
        result = await repo.create_booking(mock_create_booking_schema)
        
        mock_session.execute.assert_called_once()
        repo.add.assert_called_once_with(mock_create_booking_schema)
        
        assert result == mock_model
    
    async def test_not_exist_slots(self, repo_with_mock_add, mock_session, mock_create_booking_schema):
        mock_row = MagicMock()
        mock_row.has_slot = False
        mock_row.has_conflict = False
        
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(RoomNotFoundException):
            await repo_with_mock_add.create_booking(mock_create_booking_schema)
        
        mock_session.execute.assert_called_once()
        
        assert repo_with_mock_add.add.call_count == 0
    
    async def test_exist_conflict(self, repo_with_mock_add, mock_session, mock_create_booking_schema):
        mock_row = MagicMock()
        mock_row.has_slot = True
        mock_row.has_conflict = True
        
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(BookingAlreadyBusyException):
            await repo_with_mock_add.create_booking(mock_create_booking_schema)
            
        mock_session.execute.assert_called_once()
        
        assert repo_with_mock_add.add.call_count == 0
    
    async def test_room_busy_on_this_time(self, repo, mock_session, mock_create_booking_schema):
        mock_row = MagicMock()
        mock_row.has_slot = True
        mock_row.has_conflict = False
        
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        
        mock_session.execute.return_value = mock_result
        
        repo.add = AsyncMock()
        repo.add.side_effect = BookingRoomsObjUniquessException()
        
        with pytest.raises(BookingAlreadyBusyException):
            await repo.create_booking(mock_create_booking_schema)
        
        mock_session.execute.assert_called_once()
        repo.add.assert_called_once_with(mock_create_booking_schema)
        assert repo.add.call_count == 1

    async def test_room_not_found(self, repo, mock_session, mock_create_booking_schema):
        mock_row = MagicMock()
        mock_row.has_slot = True
        mock_row.has_conflict = False
        
        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        
        mock_session.execute.return_value = mock_result
        
        repo.add = AsyncMock()
        repo.add.side_effect = BookingRoomsInvalidObjReferences()
        
        with pytest.raises(RoomNotFoundException):
            await repo.create_booking(mock_create_booking_schema)
        
        mock_session.execute.assert_called_once()
        repo.add.assert_called_once_with(mock_create_booking_schema)
        assert repo.add.call_count == 1