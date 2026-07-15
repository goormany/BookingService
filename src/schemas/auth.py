from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenData(RefreshTokenRequest):
    access_token: str
    token_type: str | None = "bearer"

class JWTData(BaseModel):
    sub: str
    exp: int