from datetime import time, timezone

import pytest

from src.schemas.time_slots import TimeSlotsCreate, TimeSlotsIn
from src.utils.exceptions.exceptions import TimeValueValidationException


class TestTimeSlotsIn:
    @pytest.mark.parametrize("time_str,expected", [
        ("06:00", time(6, 0, tzinfo=timezone.utc)),
        ("00:00", time(0, 0, tzinfo=timezone.utc)),
        ("23:59", time(23, 59, tzinfo=timezone.utc)),
        ("12:30", time(12, 30, tzinfo=timezone.utc)),
    ])
    def test_valid_time_format(self, time_str, expected):
        data = {"start": time_str, "end": "18:00"}
        time_slot = TimeSlotsIn(**data)
        assert time_slot.start == expected

    @pytest.mark.parametrize("invalid_time", [
        "6:00", "24:00", "-1:00", "12:60", "abc", "12:00:00", ""
    ])
    def test_invalid_time_format(self, invalid_time):
        data = {"start": invalid_time, "end": "18:00"}
        with pytest.raises(ValueError):
            TimeSlotsIn(**data)
    
class TestTimeSlotsCreate:
    def test_valid_time_range(self):
        time_slot = TimeSlotsCreate(
            start=time(12, 0),
            end=time(15, 0),
            room_id=1
        )
        assert time_slot.start < time_slot.end
        
        assert time_slot.start == time(12, 0)
        assert time_slot.end == time(15, 0)
    
    @pytest.mark.parametrize(
        "start_time, end_time",
        [
            (time(10, 0), time(10, 0)),
            (time(18, 0), time(15, 0))
        ]
    )
    def test_invalid_time_range(self, start_time, end_time):
        with pytest.raises(TimeValueValidationException):
            TimeSlotsCreate(
                start=start_time,
                end=end_time,
                room_id=1
            )