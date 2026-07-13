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