from enum import StrEnum


class RedisStateEnum(StrEnum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
