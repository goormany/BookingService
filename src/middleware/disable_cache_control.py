from typing import Callable

from fastapi import Request, Response

from src.main import app

@app.middleware("http")
async def cache_control_reset(request: Request, call_next: Callable):
    response: Response = await call_next(request)
    
    response.headers["Cache-Control"] = "no-cache"
    
    return response