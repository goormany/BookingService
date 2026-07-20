from datetime import date, time, timezone

import pytest

from src.schemas.bookings import BookingCreate, BookingIn
from src.utils.exceptions.exceptions import TimeValueValidationException


class TestBookingIn:
    @pytest.mark.parametrize(
        "time_str,expected",
        [
            ("06:00", time(6, 0, tzinfo=timezone.utc)),
            ("00:00", time(0, 0, tzinfo=timezone.utc)),
            ("23:59", time(23, 59, tzinfo=timezone.utc)),
            ("12:30", time(12, 30, tzinfo=timezone.utc)),
        ],
    )
    def test_valid_time_format(self, time_str, expected):
        data = {
            "booking_date": date.today().isoformat(),
            "start_time": time_str,
            "end_time": "14:00",
        }
        booking = BookingIn(**data)
        assert booking.start_time == expected

    @pytest.mark.parametrize(
        "invalid_time", ["6:00", "24:00", "-1:00", "12:60", "abc", "12:00:00", ""]
    )
    def test_invalid_time_format(self, invalid_time):
        data = {
            "booking_date": "2026-07-18",
            "start_time": invalid_time,
            "end_time": "14:00",
        }
        with pytest.raises(ValueError):
            BookingIn(**data)

    def test_invalid_date_in_past(self):
        data = {
            "booking_date": "2020-01-01",
            "start_time": "10:00",
            "end_time": "12:00",
        }
        with pytest.raises(ValueError):
            BookingIn(**data)


class TestBookingCreate:
    def test_valid_time_range(self):
        booking = BookingCreate(
            start_time=time(12, 0),
            end_time=time(15, 0),
            booking_date=date(2026, 7, 18),
            user_id=1,
            room_id=1,
        )
        assert booking.start_time < booking.end_time

        assert booking.start_time == time(12, 0)
        assert booking.end_time == time(15, 0)

    @pytest.mark.parametrize(
        "start_time, end_time", [(time(10, 0), time(10, 0)), (time(18, 0), time(15, 0))]
    )
    def test_invalid_time_range(self, start_time, end_time):
        with pytest.raises(TimeValueValidationException):
            BookingCreate(
                start_time=start_time,
                end_time=end_time,
                booking_date=date(2026, 7, 18),
                user_id=1,
                room_id=1,
            )
