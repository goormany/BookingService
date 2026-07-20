import pytest
from datetime import date, time, timezone

from src.schemas.validators import (
    strip_not_empty,
    validate_and_convert_time,
    validate_booking_date_not_in_past,
)


class TestStripNotEmpty:
    def test_valid_string(self):
        assert strip_not_empty("hello") == "hello"

    def test_strips_whitespace(self):
        assert strip_not_empty("  hello  ") == "hello"

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="не может быть пустым"):
            strip_not_empty("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError, match="не может быть пустым"):
            strip_not_empty("   ")

    def test_non_string_raises(self):
        with pytest.raises(ValueError, match="должно быть строкой"):
            strip_not_empty(123)


class TestValidateAndConvertTime:
    @pytest.mark.parametrize(
        "time_str,expected",
        [
            ("00:00", time(0, 0, tzinfo=timezone.utc)),
            ("06:00", time(6, 0, tzinfo=timezone.utc)),
            ("12:30", time(12, 30, tzinfo=timezone.utc)),
            ("23:59", time(23, 59, tzinfo=timezone.utc)),
        ],
    )
    def test_valid_time(self, time_str, expected):
        result = validate_and_convert_time(time_str)
        assert result == expected

    @pytest.mark.parametrize(
        "invalid_time",
        [
            "6:00",
            "24:00",
            "-1:00",
            "12:60",
            "abc",
            "12:00:00",
            "",
            "25:00",
            "00:60",
        ],
    )
    def test_invalid_time_raises(self, invalid_time):
        with pytest.raises(ValueError):
            validate_and_convert_time(invalid_time)


class TestValidateBookingDateNotInPast:
    def test_today_is_valid(self):
        today = date.today()
        assert validate_booking_date_not_in_past(today) == today

    def test_future_date_is_valid(self):
        future = date.today().replace(day=date.today().day + 1)
        assert validate_booking_date_not_in_past(future) == future

    def test_past_date_raises(self):
        past = date(2020, 1, 1)
        with pytest.raises(ValueError, match="не может быть в прошлом"):
            validate_booking_date_not_in_past(past)
