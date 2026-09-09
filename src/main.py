import sys
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache

sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.api import router as api_router
from src.connectors.setup import redis_manager
from src.connectors.redis.redis_backend import SafeRedisBackend
from src.utils.cache import request_key_builder


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()

    app.state.redis_manager = redis_manager

    FastAPICache.init(
        SafeRedisBackend(redis_manager),
        prefix="fastapi-cache",
        key_builder=request_key_builder,
    )
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
