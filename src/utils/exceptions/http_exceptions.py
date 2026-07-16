from typing import Optional

from fastapi import HTTPException

class BookingRoomsHTTPException(HTTPException):
    status_code = 500
    detail = "Неожиданная ошибка"
    headers: Optional[dict[str, str]] = None
    
    def __init__(self, detail: str | None = None, status_code: int | None = None,
                 headers: Optional[dict[str, str]] = None):
        if detail is not None:
            self.detail = detail
            
        if status_code is not None:
            self.status_code = status_code
        
        if headers is not None:
            self.headers = headers
        super().__init__(status_code=self.status_code, detail=self.detail, headers=headers)
    

# USERS
class UsersUniquessHTTPException(BookingRoomsHTTPException):
    detail = "Пользователь с таким логином уже существует"
    status_code = 409

class UserNotFoundHTTPException(BookingRoomsHTTPException):
    detail = "Пользователь не найден"
    status_code = 404

class UserSoftDeleteAccountException(BookingRoomsHTTPException):
    detail = "Ваш аккаунт удален"
    status_code = 403

# AUTH
class UnauthorizedHTTPException(BookingRoomsHTTPException):
    detail = "Не удалсь авторизовать"
    status_code = 401
    headers = {"WWW-Authenticate": "Bearer"}

class InvalidCredentialsException(BookingRoomsHTTPException):
    detail = "Не верные данные авторизации"
    status_code = 401
    headers = {"WWW-Authenticate": "Bearer"}

class ForbbidenHTTPException(BookingRoomsHTTPException):
    detail = "Отказано в доступе"
    status_code = 403

# ROOMS
class RoomUniquessHTTPException(BookingRoomsHTTPException):
    detail = "Ошибка уникаольности команты"
    status_code = 409

class RoomNotFoundHTTPException(BookingRoomsHTTPException):
    detail = "Комната не найдена"
    status_code = 404
    
    
# SLOTS
class TimeSlotsUniquessHTTPException(BookingRoomsHTTPException):
    detail = "Уже есть расписание слота в этой комнату на это время"
    status_code = 409

class TimeSlotNotFoundHTTPException(BookingRoomsHTTPException):
    detail = "Временной слот не найден"
    status_code = 404

# BOOKINGS
class BookingAlreadyBusyHTTPException(BookingRoomsHTTPException):
    detail = "Комната уже забронирована на это время"
    status_code = 409

class BookingNotFoundHTTPException(BookingRoomsHTTPException):
    detail = "Бронь не найдена"
    status_code = 404