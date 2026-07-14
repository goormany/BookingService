class BookingRoomsBaseException(Exception):
    detail = "Неожиданная ошибка"
    
    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class BookingRoomsNotFoundObjException(BookingRoomsBaseException):
    detail = "Объект не найден"

class BookingRoomsObjUniquessException(BookingRoomsBaseException):
    detail = "Ошибка уникаольности объекта"

class BookingRoomsInvalidObjReferences(BookingRoomsBaseException):
    detail = "Ошибка связи объекта"