from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas.users import UserResponse, UserIn
from src.schemas.auth import RefreshTokenRequest, TokenData
from src.config import settings
from src.connectors.setup import redis_manager
from src.api.dependencies.db import DBDep
from src.api.dependencies.auth import RefreshTokenDep, get_ttl_for_redis
from src.api.dependencies.users import CurUserDep
from src.schemas.utils import BaseSuccessResponse
from src.services.users import UserService
from src.services.auth import AuthServices
from src.utils.exceptions.exceptions import (
    UserNotFoundException,
    UsersUniquessException,
    InvalidTokenDecodedException,
    ExpiredJWTTokenException,
)
from src.utils.exceptions.http_exceptions import (
    InvalidCredentialsException,
    UnauthorizedHTTPException,
    UsersUniquessHTTPException,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Регистрация нового пользователя",
    response_description="Данные созданного пользователя",
)
async def create_user(db: DBDep, user_data: UserIn):
    """
    Создаёт пользователя с указанными `username` и `password`.

    - **username**: Имя пользователя (должно быть уникальным).
    - **password**: Пароль в открытом виде (будет захeширован).

    **Возможные ошибки:**
    - `409 Conflict` — пользователь с таким username уже существует.
    """
    try:
        return await UserService(db).create_user(user_data)
    except UsersUniquessException:
        raise UsersUniquessHTTPException


@router.post(
    "/login",
    response_model=TokenData,
    status_code=200,
    summary="Аутентификация пользователя",
    response_description="JWT access_token и refresh_token",
)
async def login_user(
    db: DBDep, user_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Принимает `username` и `password`
    Возвращает пару JWT-токенов.

    - **access_token** — короткоживущий токен для доступа к API.
    - **refresh_token** — долгоживущий токен для обновления access_token.

    **Возможные ошибки:**
    - `401 Unauthorized` — неверное имя пользователя или пароль.
    """
    try:
        user = await UserService(db).get_user_with_password(username=user_data.username)
    except UserNotFoundException:
        raise InvalidCredentialsException

    if not AuthServices.verify_password(user_data.password, user.hashed_password):
        raise InvalidCredentialsException

    jwt_token = AuthServices.create_access_token(
        str(user.id), timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = AuthServices.create_access_token(
        str(user.id), timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return TokenData(access_token=jwt_token, refresh_token=refresh_token)


@router.post(
    "/logout",
    status_code=200,
    response_model=BaseSuccessResponse,
    summary="Выход из системы",
    response_description="Сообщение об успешном выходе",
)
async def logout_user(
    db: DBDep,
    user: CurUserDep,
    request: Annotated[RefreshTokenRequest, Body()],
):
    """
    Инвалидирует refresh_token (добавляет в чёрный список Redis).

    - **refresh_token**: Токен, который нужно инвалидировать.

    **Возможные ошибки:**
    - `401 Unauthorized` — токен невалиден, истёк или уже в чёрном списке.
    """
    try:
        jwt_data = AuthServices.decode_access_token(request.refresh_token)
    except (InvalidTokenDecodedException, ExpiredJWTTokenException):
        raise UnauthorizedHTTPException

    if await redis_manager.get(jwt_data.jti) is not None:
        raise UnauthorizedHTTPException

    ttl = get_ttl_for_redis(int(jwt_data.exp))
    await redis_manager.set(key=jwt_data.jti, value="blacklisted", expire=ttl)

    return BaseSuccessResponse(ok="true")


@router.post(
    "/refresh",
    response_model=TokenData,
    status_code=200,
    summary="Обновление access_token по refresh_token",
    response_description="Новая пара access_token и refresh_token",
)
async def refresh(refresh_token: RefreshTokenDep):
    """
    **Возможные ошибки:**
    - `401 Unauthorized` — refresh_token истёк, невалиден или пользователь не найден.
    """
    return refresh_token
