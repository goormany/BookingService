import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.api import router as api_router

app = FastAPI(
    debug=settings.IS_DEBUG,
    title="Сервис бронирования переговорных комнат (API)"
)
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.IS_DEBUG
    )