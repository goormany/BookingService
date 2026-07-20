from pydantic import BaseModel

from src.schemas.validators import NonEmptyStr


class RefreshTokenRequest(BaseModel):
    refresh_token: NonEmptyStr


class TokenData(RefreshTokenRequest):
    access_token: NonEmptyStr
    token_type: str | None = "bearer"


class JWTData(BaseModel):
    sub: str
    exp: int
