from pydantic import BaseModel

class BaseSuccessResponse(BaseModel):
    ok: str = True