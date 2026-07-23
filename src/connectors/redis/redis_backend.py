from typing import Optional, Tuple

from fastapi_cache.types import Backend

from src.connectors.redis.redis_manager import RedisManager


class SafeRedisBackend(Backend):
    def __init__(self, redis_manager: RedisManager):
        self._manager = redis_manager

    async def get_with_ttl(self, key: str) -> Tuple[int, bytes | None]:
        value = await self._manager.get(key)
        if value is None:
            return -2, None
        return -1, value.encode()

    async def get(self, key: str) -> bytes | None:
        value = await self._manager.get(key)
        if value is None:
            return None
        return value.encode()

    async def set(
        self, key: str, value: bytes, expire: int | None = None
    ) -> None:
        await self._manager.set(
            key, value.decode(), expire=expire
        )

    async def clear(self, namespace: str | None = None, key: str | None = None) -> int:
        if key is not None:
            return await self._manager.delete(key)
        if namespace is not None:
            return await self._manager.clear_by_pattern(namespace)
        return 0
        