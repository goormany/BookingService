from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.users import UserResponse, UserIn
from src.schemas.auth import TokenData
from src.config import settings
from src.api.dependencies.db import DBDep
from src.api.dependencies.auth import RefreshTokenDep, tokenDep
from src.services.users import UserService
from src.services.auth import AuthServices
from src.utils.exceptions.exceptions import ExpiredJWTTokenException, InvalidTokenDecodedException, UserNotFoundException, UsersUniquessException
from src.utils.exceptions.http_exceptions import InvalidCredentialsException, UnauthorizedHTTPException, UsersUniquessHTTPException

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def create_user(db: DBDep, user_data: UserIn):
    try:
        return await UserService(db).create_user(user_data)
    except UsersUniquessException:
        raise UsersUniquessHTTPException


@router.post("/login", response_model=TokenData, status_code=200)
async def login_user(db: DBDep, user_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        user = await UserService(db).get_user_with_password(username=user_data.username)
    except UserNotFoundException:
        raise InvalidCredentialsException
    
    if not AuthServices.verify_password(user_data.password, user.hashed_password):
        raise InvalidCredentialsException
    
    jwt_token = AuthServices.create_access_token(str(user.id), timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = AuthServices.create_access_token(str(user.id), timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS))
    return TokenData(access_token=jwt_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenData, status_code=200)
async def refresh(refresh_token: RefreshTokenDep):
    return refresh_token