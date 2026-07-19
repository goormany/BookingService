from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import NoResultFound

from src.data_mappers.rooms import RoomDataMapper
from src.repos.rooms import RoomRepository
from src.models.rooms import Rooms
from src.schemas.rooms import RoomWithSlotsResponse
from src.utils.exceptions.exceptions import RoomNotFoundException



    

@pytest.fixture
def repo(mock_session):
    repo = RoomRepository(mock_session)
    repo.RoomWithSlotsResponse = MagicMock()
    return repo

@pytest.fixture
def mock_model():
    return Rooms(
        id=1,
        name="room 1",
        created_at=datetime(2026, 7, 19, 12, 0, 0)
    )

class TestGetRoomWithSlots:
    async def test_success(self, repo, mock_session, mock_model):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_model
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_room_with_slots(room_id=1)
        
        assert isinstance(result, RoomWithSlotsResponse)
        mock_session.execute.assert_called_once()
    
    async def test_room_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one.side_effect = NoResultFound
        
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(RoomNotFoundException):
            await repo.get_room_with_slots(room_id=1000)
        
        mock_session.execute.assert_called_once()

class TestGetAllWithSlots:
    async def test_without_pagination(self, repo, mock_session, mock_model):
        page = None
        per_page = None
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_model]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_all_with_slots(page=page, per_page=per_page)
        
        assert len(result) == 1
        assert isinstance(result[0], RoomWithSlotsResponse)
        mock_session.execute.assert_called_once()
        
        call_args = mock_session.execute.call_args[0][0]
        
        assert call_args._limit is None
        assert call_args._offset is None

    async def test_with_pagination(self, repo, mock_session, mock_model):
        page = 3
        per_page = 10
        
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [mock_model]
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_all_with_slots(per_page=per_page, page=page)
        
        assert len(result) == 1
        assert isinstance(result[0], RoomWithSlotsResponse)
        mock_session.execute.assert_called_once()
        
        call_args = mock_session.execute.call_args[0][0]
        
        assert call_args._limit is not None
        assert call_args._offset is not None
        
        assert call_args._limit == per_page
        assert call_args._offset == (page-1)*per_page