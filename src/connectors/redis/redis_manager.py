import asyncio

import redis.asyncio as redis
from redis.exceptions import TimeoutError as RedisTimeoutError
from redis.exceptions import ConnectionError as RedisConnectionError

from src.utils.enums.redis_state import RedisStateEnum

RECONNECT_BASE_DELAY = 10
RECONNECT_MAX_DELAY = 300
REDIS_TIMEOUT = 0.5


class RedisManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis: redis.Redis | None = None
        self._state: RedisStateEnum = RedisStateEnum.DISCONNECTED
        self._reconnect_task: asyncio.Task | None = None
        self._reconnect_delay = RECONNECT_BASE_DELAY
        self._lock = asyncio.Lock()

    @property
    def state(self) -> RedisStateEnum:
        return self._state

    async def connect(self) -> None:
        async with self._lock:
            if self._state == RedisStateEnum.CONNECTED:
                return
            try:
                self.redis = await redis.from_url(
                    self.redis_url,
                    socket_connect_timeout=REDIS_TIMEOUT,
                    socket_timeout=REDIS_TIMEOUT,
                )
                await self.redis.ping()
                self._state = RedisStateEnum.CONNECTED
                self._reconnect_delay = RECONNECT_BASE_DELAY
            except (RedisTimeoutError, RedisConnectionError, OSError):
                self._state = RedisStateEnum.DISCONNECTED
                self.redis = None
                self._start_reconnect()

    async def close(self) -> None:
        self._stop_reconnect()
        async with self._lock:
            if self.redis:
                try:
                    await self.redis.aclose()
                except Exception:
                    pass
                self.redis = None
            self._state = RedisStateEnum.DISCONNECTED

    async def set(
        self, key: str, value: str, expire: int | None = None
    ) -> None:
        if self._state != RedisStateEnum.CONNECTED or self.redis is None:
            return
        try:
            if expire is not None:
                await self.redis.set(name=key, value=value, ex=expire)
            else:
                await self.redis.set(name=key, value=value)
        except (RedisTimeoutError, RedisConnectionError, OSError):
            await self._on_connection_lost()

    async def get(self, key: str) -> str | None:
        if self._state != RedisStateEnum.CONNECTED or self.redis is None:
            return None
        try:
            value = await self.redis.get(name=key)
            return value.decode() if value is not None else None
        except (RedisTimeoutError, RedisConnectionError, OSError):
            await self._on_connection_lost()
            return None

    async def delete(self, key: str) -> None:
        if self._state != RedisStateEnum.CONNECTED or self.redis is None:
            return
        try:
            await self.redis.delete(key)
        except (RedisTimeoutError, RedisConnectionError, OSError):
            await self._on_connection_lost()

    async def _on_connection_lost(self) -> None:
        async with self._lock:
            if self._state == RedisStateEnum.DISCONNECTED:
                return
            self._state = RedisStateEnum.DISCONNECTED
            self.redis = None
        self._start_reconnect()

    def _start_reconnect(self) -> None:
        if self._reconnect_task is None or self._reconnect_task.done():
            self._reconnect_task = asyncio.create_task(self._reconnect_loop())

    def _stop_reconnect(self) -> None:
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
        self._reconnect_task = None

    async def _reconnect_loop(self) -> None:
        while True:
            await asyncio.sleep(self._reconnect_delay)
            try:
                new_redis = await redis.from_url(
                    self.redis_url,
                    socket_connect_timeout=REDIS_TIMEOUT,
                    socket_timeout=REDIS_TIMEOUT,
                )
                await new_redis.ping()
                async with self._lock:
                    self.redis = new_redis
                    self._state = RedisStateEnum.CONNECTED
                    self._reconnect_delay = RECONNECT_BASE_DELAY
                return
            except (RedisTimeoutError, RedisConnectionError, OSError):
                self._reconnect_delay = min(
                    self._reconnect_delay * 2, RECONNECT_MAX_DELAY
                )

    async def clear_by_pattern(self, pattern: str) -> int:
        if self._state != RedisStateEnum.CONNECTED or self.redis is None:
            return 0
        try:
            lua = f"for i, name in ipairs(redis.call('KEYS', '{pattern}:*')) do redis.call('DEL', name); end"
            return await self.redis.eval(lua, numkeys=0)
        except (RedisTimeoutError, RedisConnectionError, OSError):
            await self._on_connection_lost()
            return 0