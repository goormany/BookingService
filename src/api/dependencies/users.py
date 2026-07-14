from typing import Annotated

from fastapi import Depends

from src.api.dependencies.auth import tokenDep
from src.api.dependencies.db import DBDep
from src.schemas.users import UserResponse
from src.services.auth import AuthServices
from src.services.users import UserService
from src.utils.exceptions.exceptions import ExpiredJWTTokenException, InvalidTokenDecodedException, UserNotFoundException
from src.utils.exceptions.http_exceptions import UnauthorizedHTTPException

async def get_current_user(db:DBDep, token: tokenDep) -> UserResponse:
    try:
        jwt_data = AuthServices.decode_access_token(token)
    except (InvalidTokenDecodedException, ExpiredJWTTokenException):
        raise UnauthorizedHTTPException
    user_id = int(jwt_data.sub)
    
    try:
        return await UserService(db).get_user(id=user_id)
    except UserNotFoundException:
        raise UnauthorizedHTTPException

CurUserDep = Annotated[UserResponse, Depends(get_current_user)]
    