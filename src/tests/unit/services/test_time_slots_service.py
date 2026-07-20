from unittest.mock import AsyncMock, patch

import pytest

from src.schemas.time_slots import TimeSlotsCreate, TimeSlotsIn
from src.services.time_slots import TimeSlotService
from src.models.time_slots import TimeSlots
from src.utils.exceptions.exceptions import (
    BookingRoomsInvalidObjReferences,
    BookingRoomsNotFoundObjException,
    BookingRoomsObjUniquessException,
    RoomNotFoundException,
    TimeSlotNotFoundException,
    TimeSlotsUniquessException,
    TimeValueValidationException,
)


@pytest.fixture
def service():
    db = AsyncMock()
    db.time_slots = AsyncMock()
    return TimeSlotService(db)


@pytest.fixture
def args():
    return (TimeSlots.room_id == 1,)


@pytest.fixture
def kwargs():
    return {"id": 1}


class TestCreateSlot:
    @pytest.fixture
    def time_slot_in(self):
        return TimeSlotsIn(start="15:00", end="18:00")

    async def test_success(self, service, time_slot_in):
        service.db.time_slots.add.return_value = "slot"
        room_id = 1

        result = await service.create_slot(time_slot_in, room_id=room_id)

        assert isinstance(result, str)
        assert result == "slot"

        service.db.time_slots.add.assert_called_once_with(
            TimeSlotsCreate(**time_slot_in.model_dump(), room_id=room_id)
        )
        service.db.commit.assert_called_once()

    async def test_invalid_time_format(self, service, time_slot_in):
        room_id = 1

        with patch("src.services.time_slots.TimeSlotsCreate") as mock_time_slots_create:
            mock_time_slots_create.side_effect = TimeValueValidationException()

            with pytest.raises(TimeValueValidationException):
                await service.create_slot(time_slot_in, room_id)

            service.db.time_slots.create_slot.assert_not_called()
            service.db.commit.assert_not_called()

    async def test_room_not_found(self, service, time_slot_in):
        service.db.time_slots.add.side_effect = BookingRoomsInvalidObjReferences()
        room_id = 1

        with pytest.raises(RoomNotFoundException):
            await service.create_slot(time_slot_in, room_id)

        service.db.time_slots.add.assert_called_once_with(
            TimeSlotsCreate(**time_slot_in.model_dump(), room_id=room_id)
        )
        service.db.commit.assert_not_called()

    async def test_unique_error(self, service, time_slot_in):
        service.db.time_slots.add.side_effect = BookingRoomsObjUniquessException()
        room_id = 1

        with pytest.raises(TimeSlotsUniquessException):
            await service.create_slot(time_slot_in, room_id)

        service.db.time_slots.add.assert_called_once_with(
            TimeSlotsCreate(**time_slot_in.model_dump(), room_id=room_id)
        )
        service.db.commit.assert_not_called()


class TestDeleteSlot:
    async def test_success(self, service, args, kwargs):
        service.db.time_slots.delete.return_value = "del_slot"

        result = await service.delete_slot(*args, **kwargs)

        assert result == "del_slot"

        service.db.time_slots.delete.assert_called_once_with(*args, **kwargs)
        service.db.commit.assert_called_once()

    async def test_time_slot_not_found(self, service, args, kwargs):
        service.db.time_slots.delete.side_effect = BookingRoomsNotFoundObjException()

        with pytest.raises(TimeSlotNotFoundException):
            await service.delete_slot(*args, **kwargs)

        service.db.time_slots.delete.assert_called_once_with(*args, **kwargs)
        service.db.commit.assert_not_called()


class TestGetAll:
    async def test_success(self, service):
        service.db.time_slots.get_all.return_value = ["time_slot"]

        result = await service.get_all()

        assert result == ["time_slot"]

        service.db.time_slots.get_all.assert_called_once()

    async def test_success_empty_list(self, service):
        service.db.time_slots.get_all.return_value = []

        result = await service.get_all()

        assert result == []

        service.db.time_slots.get_all.assert_called_once()
