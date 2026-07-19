from unittest.mock import AsyncMock

import pytest

from src.schemas.rooms import RoomCreate, RoomUpdate
from src.services.rooms import RoomService
from src.models.rooms import Rooms
from src.utils.exceptions.exceptions import BookingRoomsNotFoundObjException, BookingRoomsObjUniquessException, RoomNotFoundException, RoomUniquessException


@pytest.fixture
def service():
    db = AsyncMock()
    db.rooms = AsyncMock()
    return RoomService(db)

@pytest.fixture
def room_in():
    return RoomCreate(
        name="test name"
    )
    
@pytest.fixture
def args():
    return (Rooms.name == "test",)

@pytest.fixture
def kwargs():
    return {"id": 1}

class TestGetAll:
    async def test_without_pagination(self, service):
        service.db.rooms.get_all.return_value = ["room1", "room2"]
        
        page = None
        per_page = None
        
        result = await service.get_all(per_page=per_page, page=page)
        assert isinstance(result, list)
        assert result == ["room1", "room2"]
        assert result[0] == "room1"
        assert result[1] == "room2"
        
        service.db.rooms.get_all.assert_called_once()
        
        call_args = service.db.rooms.get_all.call_args
        assert call_args.kwargs["per_page"] is None
        assert call_args.kwargs["page"] is None

    async def test_with_pagination(self, service):
        service.db.rooms.get_all.return_value = ["room1", "room2"]
        
        page = 5
        per_page = 3
        
        result = await service.get_all(per_page=per_page, page=page)
        assert isinstance(result, list)
        assert result == ["room1", "room2"]
        assert result[0] == "room1"
        assert result[1] == "room2"
        
        service.db.rooms.get_all.assert_called_once()
        
        call_args = service.db.rooms.get_all.call_args
        assert call_args.kwargs["per_page"] == per_page
        assert call_args.kwargs["page"] == page

class TestCreate:
    async def test_success(self, service, room_in):
        service.db.rooms.add.return_value = "room"
        
        result = await service.create(room_in)
        
        assert isinstance(result, str)
        assert result == "room"
        
        service.db.rooms.add.assert_called_once_with(room_in)
        service.db.commit.assert_called_once()

    async def test_uniques_error(self, service, room_in):
        service.db.rooms.add.side_effect = BookingRoomsObjUniquessException()
        
        with pytest.raises(RoomUniquessException):
            await service.create(room_in)
        
        service.db.rooms.add.assert_called_once_with(room_in)
        service.db.commit.assert_not_called()

class TestGetRoom:
    async def test_success(self, service, args, kwargs):
        service.db.rooms.get_one.return_value = "room"
        
        result = await service.get_room(*args, **kwargs)
        
        assert isinstance(result, str)
        assert result == "room"
        
        service.db.rooms.get_one.assert_called_once_with(*args, **kwargs)

    async def test_not_found(self, service, args, kwargs):
        service.db.rooms.get_one.side_effect = BookingRoomsNotFoundObjException()
        
        with pytest.raises(RoomNotFoundException):
            await service.get_room(*args, **kwargs)
        
        service.db.rooms.get_one.assert_called_once_with(*args, **kwargs)

class TestGetRoomWithSlots:
    async def test_success(self, service):
        service.db.rooms.get_room_with_slots.return_value = "room"
        room_id = 1
        
        result = await service.get_room_with_slots(room_id=room_id)
        
        assert isinstance(result, str)
        assert result == "room"
        
        service.db.rooms.get_room_with_slots.assert_called_once_with(room_id)

    async def test_not_found(self, service):
        service.db.rooms.get_room_with_slots.side_effect = RoomNotFoundException()
        room_id = 1
        
        with pytest.raises(RoomNotFoundException):
            await service.get_room_with_slots(room_id=room_id)
        
        service.db.rooms.get_room_with_slots.assert_called_once_with(room_id)
        
    
class TestUpdateRoom:
    async def test_success(self, service, args, kwargs):
        service.db.rooms.edit.return_value = "room"
        
        room_upd = RoomUpdate(description="new desc")
        
        result = await service.update_room(
            room_upd,
            *args,
            **kwargs
        )
        
        assert isinstance(result, str)
        assert result == "room"
        
        service.db.rooms.edit.assert_called_once_with(room_upd, True, *args, **kwargs)
        service.db.commit.assert_called_once()

    async def test_not_found_room(self, service, args, kwargs):
        service.db.rooms.edit.side_effect = BookingRoomsNotFoundObjException
        
        room_upd = RoomUpdate(description="new desc")
        
        with pytest.raises(RoomNotFoundException):
            await service.update_room(
            room_upd,
                *args,
                **kwargs
            )
        
        service.db.rooms.edit.assert_called_once_with(room_upd, True, *args, **kwargs)
        service.db.commit.assert_not_called()

    async def test_unique_room_error(self, service, args, kwargs):
        service.db.rooms.edit.side_effect = BookingRoomsObjUniquessException
        
        room_upd = RoomUpdate(description="new desc")
        
        with pytest.raises(RoomUniquessException):
            await service.update_room(
            room_upd,
                *args,
                **kwargs
            )
        
        service.db.rooms.edit.assert_called_once_with(room_upd, True, *args, **kwargs)
        service.db.commit.assert_not_called()

class TestDeleteRoom:
    async def test_success(self, service, args, kwargs):
        service.db.rooms.delete.return_value = "del_room"
        
        result = await service.delete_room(*args, **kwargs)
        
        assert isinstance(result, str)
        assert result == "del_room"
        
        service.db.rooms.delete.assert_called_once_with(*args, **kwargs)
        service.db.commit.assert_called_once()

    async def test_room_not_found(self, service, args, kwargs):
        service.db.rooms.delete.side_effect = BookingRoomsNotFoundObjException
        
        with pytest.raises(RoomNotFoundException):
            await service.delete_room(*args, **kwargs)
        
        service.db.rooms.delete.assert_called_once_with(*args, **kwargs)
        service.db.commit.assert_not_called()