import sys
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.api import router as api_router
from src.connectors.setup import redis_manager
from src.utils.cache import request_key_builder


@asynccontextmanager
async def lifespan(_: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache", key_builder=request_key_builder)
    yield
    await redis_manager.close()


app = FastAPI(
    debug=settings.IS_DEBUG,
    title="Сервис бронирования переговорных комнат (API)",
    lifespan=lifespan,
)
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.IS_DEBUG,
    )
