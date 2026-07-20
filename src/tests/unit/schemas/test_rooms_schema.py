import pytest
from pydantic import ValidationError

from src.schemas.rooms import RoomCreate, RoomUpdate

class TestRoomCreate:
    def test_required_name(self):
        room = RoomCreate(name="room 1")
        assert room.name == "room 1"
        assert room.description is None

    def test_with_description(self):
        room = RoomCreate(name="room 1", description="big room")
        assert room.description == "big room"

    @pytest.mark.parametrize("value", ["", "   "])
    def test_invalid_empty_name(self, value):
        with pytest.raises(ValidationError):
            RoomCreate(name=value)

class TestRoomUpdate:
    def test_all_optional(self):
        room = RoomUpdate()
        assert room.name is None
        assert room.description is None

    def test_partial_update(self):
        room = RoomUpdate(name="backrooms")
        assert room.name == "backrooms"
        assert room.description is None

    @pytest.mark.parametrize("value", ["", "   "])
    def test_invalid_empty_name(self, value):
        with pytest.raises(ValidationError):
            RoomUpdate(name=value)
