from datetime import date, datetime, time
from unittest.mock import AsyncMock, patch

import pytest

from src.schemas.bookings import AvailabilityResponse, BookingIn, FreeInterval
from src.schemas.time_slots import TimeSlotsResponse
from src.services.bookings import BookingService
from src.schemas.rooms import RoomWithSlotsResponse
from src.utils.exceptions.exceptions import (
    BookingAlreadyBusyException,
    BookingNotFoundException,
    BookingRoomsNotFoundObjException,
    RoomNotFoundException,
    TimeValueValidationException,
)


class Slot:
    def __init__(self, start: time, end: time):
        self.start = start
        self.end = end


@pytest.fixture
def mock_room_with_slots():
    return RoomWithSlotsResponse(
        id=1,
        name="test room",
        slots=[
            TimeSlotsResponse(
                id=1,
                start=time(12, 0),
                end=time(15, 0),
                room_id=1,
                created_at=datetime(2026, 7, 19, 12, 0),
            )
        ],
    )


@pytest.fixture
def service():
    db = AsyncMock()
    db.bookings = AsyncMock()
    db.rooms = AsyncMock()
    return BookingService(db)


class TestComputeFreeSlots:
    def setup_method(self):
        self.service = BookingService(db=None)

    def test_no_bookings_full_slot_free(self):
        slots = [Slot(time(9, 0), time(18, 0))]
        booked = []
        result = self.service._compute_free_slots(slots, booked)

        assert len(result) == 1
        assert result[0] == FreeInterval(start_time=time(9, 0), end_time=time(18, 0))

    def test_full_slot_booked_no_free_slots(self):
        slots = [Slot(time(9, 0), time(18, 0))]
        booked = [(time(9, 0), time(18, 0))]
        result = self.service._compute_free_slots(slots, booked)

        assert result == []

    def test_booking_at_start_of_slot(self):
        slots = [Slot(time(9, 0), time(18, 0))]
        booked = [(time(9, 0), time(12, 0))]
        result = self.service._compute_free_slots(slots, booked)

        assert len(result) == 1
        assert result[0] == FreeInterval(start_time=time(12, 0), end_time=time(18, 0))

    def test_booking_at_end_of_slot(self):
        slots = [Slot(time(9, 0), time(18, 0))]
        booked = [(time(15, 0), time(18, 0))]
        result = self.service._compute_free_slots(slots, booked)

        assert len(result) == 1
        assert result[0] == FreeInterval(start_time=time(9, 0), end_time=time(15, 0))

    def test_booking_in_middle_of_slot(self):
        slots = [Slot(time(9, 0), time(18, 0))]
        booked = [(time(12, 0), time(14, 0))]
        result = self.service._compute_free_slots(slots, booked)

        assert len(result) == 2
        assert result[0] == FreeInterval(start_time=time(9, 0), end_time=time(12, 0))
        assert result[1] == FreeInterval(start_time=time(14, 0), end_time=time(18, 0))

    def test_multiple_bookings_in_slot(self):
        """Несколько несмежных броней в одном слоте."""
        slots = [Slot(time(8, 0), time(20, 0))]
        booked = [
            (time(9, 0), time(11, 0)),
            (time(13, 0), time(15, 0)),
            (time(17, 0), time(19, 0)),
        ]
        result = self.service._compute_free_slots(slots, booked)

        assert len(result) == 4
        assert result[0] == FreeInterval(start_time=time(8, 0), end_time=time(9, 0))
        assert result[1] == FreeInterval(start_time=time(11, 0), end_time=time(13, 0))
        assert result[2] == FreeInterval(start_time=time(15, 0), end_time=time(17, 0))
        assert result[3] == FreeInterval(start_time=time(19, 0), end_time=time(20, 0))

    def test_multiple_slots_no_bookings(self):
        slots = [
            Slot(time(9, 0), time(12, 0)),
            Slot(time(13, 0), time(18, 0)),
        ]
        booked = []
        result = self.service._compute_free_slots(slots, booked)

        assert len(result) == 2
        assert result[0] == FreeInterval(start_time=time(9, 0), end_time=time(12, 0))
        assert result[1] == FreeInterval(start_time=time(13, 0), end_time=time(18, 0))

    def test_multiple_slots_with_bookings(self):
        slots = [
            Slot(time(9, 0), time(12, 0)),
            Slot(time(13, 0), time(18, 0)),
        ]
        booked = [
            (time(10, 0), time(11, 0)),
            (time(14, 0), time(16, 0)),
        ]
        result = self.service._compute_free_slots(slots, booked)

        assert len(result) == 4
        # Первый слот: 9:00-10:00, 11:00-12:00
        assert result[0] == FreeInterval(start_time=time(9, 0), end_time=time(10, 0))
        assert result[1] == FreeInterval(start_time=time(11, 0), end_time=time(12, 0))
        # Второй слот: 13:00-14:00, 16:00-18:00
        assert result[2] == FreeInterval(start_time=time(13, 0), end_time=time(14, 0))
        assert result[3] == FreeInterval(start_time=time(16, 0), end_time=time(18, 0))

    def test_empty_slots_list(self):
        slots = []
        booked = [(time(10, 0), time(12, 0))]
        result = self.service._compute_free_slots(slots, booked)

        assert result == []

    def test_zero_length_slot(self):
        slots = [Slot(time(10, 0), time(10, 0))]
        booked = []
        result = self.service._compute_free_slots(slots, booked)

        assert result == []


class TestGetAvailability:
    async def test_success_with_room_id(self, service, mock_room_with_slots):
        room_id = 1
        service.db.rooms.get_room_with_slots.return_value = mock_room_with_slots
        service.db.bookings.get_active_bookings_by_date = AsyncMock(return_value=[])

        result = await service.get_availability(date(2026, 7, 19), room_id=room_id)

        assert isinstance(result, AvailabilityResponse)
        assert result.date == date(2026, 7, 19)

        service.db.rooms.get_room_with_slots.assert_called_once_with(room_id)

    async def test_success_without_room_id(self, service, mock_room_with_slots):
        service.db.rooms.get_all_with_slots.return_value = [mock_room_with_slots]
        service.db.bookings.get_active_bookings_by_date = AsyncMock(return_value=[])

        result = await service.get_availability(date(2026, 7, 19))

        assert isinstance(result, AvailabilityResponse)
        assert result.date == date(2026, 7, 19)

        service.db.rooms.get_all_with_slots.assert_called_once()

    async def test_room_not_found(self, service):
        service.db.rooms.get_room_with_slots.side_effect = RoomNotFoundException

        with pytest.raises(RoomNotFoundException):
            await service.get_availability(date(2026, 7, 19), room_id=1)

        service.db.rooms.get_room_with_slots.assert_called_once_with(1)


class TestCreateBooking:
    @pytest.fixture
    def booking_in(self):
        return BookingIn(
            booking_date=date.today(), start_time="12:00", end_time="15:00"
        )

    async def test_success(self, service, booking_in):
        room_id = 1
        user_id = 1
        service.db.bookings.create_booking.return_value = "booking_response"

        result = await service.create_booking(booking_in, room_id, user_id)

        assert isinstance(result, str)
        assert result == "booking_response"
        service.db.bookings.create_booking.assert_called_once()

    async def test_invalid_time_format(self, service, booking_in):
        room_id = 1
        user_id = 1

        with patch("src.services.bookings.BookingCreate") as mock_booking_create:
            mock_booking_create.side_effect = TimeValueValidationException()

            with pytest.raises(TimeValueValidationException):
                await service.create_booking(booking_in, room_id, user_id)

            service.db.bookings.create_booking.assert_not_called()
            service.db.commit.assert_not_called()

    async def test_busy_room_now(self, service, booking_in):
        service.db.bookings.create_booking.side_effect = BookingAlreadyBusyException()

        with pytest.raises(BookingAlreadyBusyException):
            await service.create_booking(booking_in, 1, 1)

        service.db.bookings.create_booking.assert_called_once()
        service.db.commit.assert_not_called()

    async def test_room_not_found(self, service, booking_in):
        service.db.bookings.create_booking.side_effect = RoomNotFoundException()

        with pytest.raises(RoomNotFoundException):
            await service.create_booking(booking_in, 1, 1)

        service.db.bookings.create_booking.assert_called_once()

        service.db.commit.assert_not_called()


class TestGetMyBookings:
    async def test_without_pagination(self, service):
        service.db.bookings.get_filtred.return_value = ["booking_reponse"]
        page = None
        per_page = None
        user_id = 1

        result = await service.get_my_bookings(
            per_page=per_page, page=page, user_id=user_id
        )

        assert isinstance(result, list)
        assert result == ["booking_reponse"]

        call_args = service.db.bookings.get_filtred.call_args

        assert call_args.kwargs["per_page"] is None
        assert call_args.kwargs["page"] is None
        assert call_args.kwargs["user_id"] == user_id

    async def test_with_pagination(self, service):
        service.db.bookings.get_filtred.return_value = ["booking_reponse"]
        page = 3
        per_page = 5
        user_id = 1

        result = await service.get_my_bookings(
            per_page=per_page, page=page, user_id=user_id
        )

        assert isinstance(result, list)
        assert result == ["booking_reponse"]

        call_args = service.db.bookings.get_filtred.call_args

        assert call_args.kwargs["per_page"] == per_page
        assert call_args.kwargs["page"] == page
        assert call_args.kwargs["user_id"] == user_id


class TestSoftDeleteBooking:
    async def test_success(self, service):
        service.db.bookings.edit.return_value = "edited_booking"

        result = await service.soft_delete_booking()

        assert isinstance(result, str)
        assert result == "edited_booking"

        service.db.bookings.edit.assert_called_once()
        service.db.commit.assert_called_once()

    async def test_booking_not_found(self, service):
        service.db.bookings.edit.side_effect = BookingRoomsNotFoundObjException()

        with pytest.raises(BookingNotFoundException):
            await service.soft_delete_booking()

        service.db.bookings.edit.assert_called_once()
        service.db.commit.assert_not_called()
