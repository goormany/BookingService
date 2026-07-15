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

# AUTH
class UnauthorizedHTTPException(BookingRoomsHTTPException):
    detail = "Не удалсь авторизовать"
    status_code = 401
    headers = {"WWW-Authenticate": "Bearer"}

class InvalidCredentialsException(BookingRoomsHTTPException):
    detail = "Не верные данные авторизации"
    status_code = 401
    headers = {"WWW-Authenticate": "Bearer"}


# ROOMS
class RoomUniquessHTTPException(BookingRoomsHTTPException):
    detail = "Ошибка уникаольности команты"
    status_code = 409

class RoomNotFoundHTTPException(BookingRoomsHTTPException):
    detail = "Комната не найдена"
    status_code = 404