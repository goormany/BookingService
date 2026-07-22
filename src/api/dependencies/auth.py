from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Body, Depends
from fastapi.security import OAuth2PasswordBearer

from src.config import settings
from src.connectors.setup import redis_manager
from src.api.dependencies.db import DBDep
from src.schemas.auth import RefreshTokenRequest, TokenData
from src.services.auth import AuthServices
from src.services.users import UserService
from src.utils.exceptions.exceptions import (
    ExpiredJWTTokenException,
    InvalidTokenDecodedException,
    UserNotFoundException,
)
from src.utils.exceptions.http_exceptions import UnauthorizedHTTPException

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login", refreshUrl="api/v1/auth/refresh"
)
tokenDep = Annotated[str, Depends(oauth2_scheme)]

def get_ttl_for_redis(jwt_expire_time: int):
    return jwt_expire_time - int(datetime.now(timezone.utc).timestamp())

async def refresh_token(
    db: DBDep, request: Annotated[RefreshTokenRequest, Body()]
) -> TokenData:
    refresh_token = request.refresh_token
    try:
        jwt_data = AuthServices.decode_access_token(refresh_token)
    except (InvalidTokenDecodedException, ExpiredJWTTokenException):
        raise UnauthorizedHTTPException

    if await redis_manager.get(jwt_data.jti) is not None:
        raise UnauthorizedHTTPException

    user_id = int(jwt_data.sub)

    try:
        await UserService(db).get_user(id=user_id)
    except UserNotFoundException:
        raise UnauthorizedHTTPException

    new_access_token = AuthServices.create_access_token(
        str(user_id), timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = AuthServices.create_access_token(
        str(user_id), timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    ttl = get_ttl_for_redis(int(jwt_data.exp))
    await redis_manager.set(key=jwt_data.jti, value="refreshed_token", expire=ttl)
    
    return TokenData(access_token=new_access_token, refresh_token=new_refresh_token)


RefreshTokenDep = Annotated[TokenData, Depends(refresh_token)]
