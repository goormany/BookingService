import redis.asyncio as redis


class RedisManager:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis = None

    async def connect(self):
        self.redis = await redis.from_url(self.redis_url)

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def set(self, key: str, value: str, expire: int | None = None):
        if expire:
            await self.redis.set(name=key, value=value, ex=expire)
        else:
            await self.redis.set(name=key, value=value)

    async def get(self, key: str):
        return await self.redis.get(name=key)

    async def delete(self, key: str):
        await self.redis.delete(key)