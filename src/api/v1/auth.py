from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.users import UserResponse, UserIn
from src.schemas.auth import TokenData
from src.api.dependencies.db import DBDep
from src.services.users import UserService
from src.services.auth import AuthServices
from src.utils.exceptions.exceptions import UserNotFoundException, UsersUniquessException
from src.utils.exceptions.http_exceptions import InvalidCredentialsException, UsersUniquessHTTPException

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
    
    token = AuthServices.create_access_token({"sub": str(user.id)})
    return TokenData(access_token=token)