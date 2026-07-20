import re
from datetime import date, time, timezone
from typing import Annotated

from pydantic import BeforeValidator


def strip_not_empty(v: str) -> str:
    if not isinstance(v, str):
        raise ValueError("Значение должно быть строкой")
    stripped = v.strip()
    if not stripped:
        raise ValueError("Значение не может быть пустым или состоять только из пробелов")
    return stripped


NonEmptyStr = Annotated[str, BeforeValidator(strip_not_empty)]


def validate_and_convert_time(v: str) -> time:
    if not re.match(r'^\d{2}:\d{2}$', v):
        raise ValueError(f'Время должно быть в формате HH:MM, получено {v}')

    hours, minutes = map(int, v.split(':'))
    if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
        raise ValueError(f'Неверное время: {v}')

    return time(hours, minutes, tzinfo=timezone.utc)


def validate_booking_date_not_in_past(v: date) -> date:
    if v < date.today():
        raise ValueError(f'Дата бронирования не может быть в прошлом: {v}')
    return v