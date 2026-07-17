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
    
class InvalidTokenDecodedException(BookingRoomsBaseException):
    detail = "Ошибка декодирования токена"
    
class ExpiredJWTTokenException(BookingRoomsBaseException):
    detail = "Истечение срока жизни токена"
    

# USERS
class UsersUniquessException(BookingRoomsBaseException):
    detail = "Ошибка уникальности пользователя"

class UserNotFoundException(BookingRoomsBaseException):
    detail = "Пользователь не найден"

# ROOMS
class RoomUniquessException(BookingRoomsBaseException):
    detail = "Ошибка уникальности комнаты"
    
class RoomNotFoundException(BookingRoomsNotFoundObjException):
    detail = "Комната не найдена"
    

# SLOTS
class TimeSlotsUniquessException(BookingRoomsBaseException):
    detail = "Комната имеет расписание на это время"

class TimeSlotNotFoundException(BookingRoomsBaseException):
    detail = "Временой слот не найден"
    

# BOOKINGS
class BookingAlreadyBusyException(BookingRoomsBaseException):
    detail = "Комната уже забронирован на это время"

class BookingNotFoundException(BookingRoomsBaseException):
    detail = "Бронь не найдена"
    
# CONNECTIONS
class BookingNotConnDBException(BookingRoomsBaseException):
    detail = "Нет связи с базой данных"
    
# UTILS
class TimeValueValidationException(BookingRoomsBaseException):
    detail = "Не верный промежуток времени"