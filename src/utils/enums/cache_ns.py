from enum import StrEnum

class CacheNSEnum(StrEnum):
    ALL_USERS = "get_all_users"
    ALL_ROOMS = "get_all_rooms"
    BOOKINGS_BY_ROOM_ID = "get_all_bookings_by_room_id"
    ALL_BOOKINGS = "get_all_bookings"
    AVAILABILITY = "availability"