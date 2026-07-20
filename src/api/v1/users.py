from typing import Annotated

from fastapi import APIRouter, Depends, Path

from src.schemas.users import UserResponse, UserRoleSchema
from src.services.users import UserService
from src.api.dependencies.db import DBDep
from src.api.dependencies.users import CurUserDep, get_admin_user
from src.api.dependencies.paginations import PaginationDep
from src.utils.exceptions.exceptions import UserNotFoundException
from src.utils.exceptions.http_exceptions import UserNotFoundHTTPException

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=200,
    dependencies=[Depends(get_admin_user)],
    summary="Получить список всех пользователей",
    response_description="Список пользователей с пагинацией",
)
async def get_all_users(db: DBDep, pd: PaginationDep):
    """
    Возвращает список всех зарегистрированных пользователей с пагинацией.

    - **page**: Номер страницы (по умолч. 1).
    - **per_page**: Количество записей на странице (по умолч. 20, макс. 20).

    Доступ: admin.
    """
    return await UserService(db).get_all(per_page=pd.per_page, page=pd.page)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=200,
    summary="Получить данные текущего пользователя",
    response_description="Данные аутентифицированного пользователя",
)
async def get_user_me(user_data: CurUserDep):
    """
    Возвращает данные пользователя, от имени которого выполнен запрос.

    Доступ: любой аутентифицированный пользователь.
    """
    return user_data


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=200,
    dependencies=[Depends(get_admin_user)],
    summary="Получить пользователя по ID",
    response_description="Данные пользователя",
)
async def get_user_by_id(db: DBDep, user_id: Annotated[int, Path(ge=0)]):
    """
    Возвращает данные пользователя по его ID.

    - **user_id**: ID пользователя (>= 0).

    **Возможные ошибки:**
    - `404 Not Found` — пользователь с указанным ID не найден.

    Доступ: admin.
    """
    try:
        return await UserService(db).get_user(id=user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException


@router.patch(
    "/{user_id}",
    status_code=200,
    response_model=UserResponse,
    dependencies=[Depends(get_admin_user)],
    summary="Изменить роль пользователя",
    response_description="Обновлённые данные пользователя",
)
async def change_user_role(db: DBDep, user_id: Annotated[int, Path(ge=0)], role: UserRoleSchema):
    """
    Изменяет роль пользователя.

    - **user_id**: ID пользователя (>= 0).
    - **role**: Новая роль (`admin` или `employee`).

    **Возможные ошибки:**
    - `404 Not Found` — пользователь с указанным ID не найден.

    Доступ: admin.
    """
    try:
        return await UserService(db).change_user_role(user_id, role)
    except UserNotFoundException:
        raise UserNotFoundHTTPException


@router.delete(
    "/{user_id}",
    response_model=UserResponse,
    status_code=200,
    dependencies=[Depends(get_admin_user)],
    summary="Мягко удалить пользователя",
    response_description="Данные удалённого пользователя",
)
async def soft_delete_user(db: DBDep, user_id: Annotated[int, Path(ge=0)]):
    """
    Мягкое удаление пользователя (устанавливает `is_active = False`).

    - **user_id**: ID пользователя (>= 0).

    **Возможные ошибки:**
    - `404 Not Found` — пользователь с указанным ID не найден.

    Доступ: admin.
    """
    try:
        return await UserService(db).soft_delete(user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException


@router.delete(
    "/{user_id}/hard",
    response_model=UserResponse,
    status_code=200,
    dependencies=[Depends(get_admin_user)],
    summary="Полностью удалить пользователя",
    response_description="Данные удалённого пользователя",
)
async def hard_delete_user(db: DBDep, user_id: Annotated[int, Path(ge=0)]):
    """
    Полное (жёсткое) удаление пользователя из базы данных.

    - **user_id**: ID пользователя (>= 0).

    **Возможные ошибки:**
    - `404 Not Found` — пользователь с указанным ID не найден.

    Доступ: admin.
    """
    try:
        return await UserService(db).hard_delete(user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException


@router.patch(
    "/{user_id}/restore",
    status_code=200,
    response_model=UserResponse,
    dependencies=[Depends(get_admin_user)],
    summary="Восстановить мягко удалённого пользователя",
    response_description="Данные восстановленного пользователя",
)
async def restore_user(db: DBDep, user_id: Annotated[int, Path(ge=0)]):
    """
    Восстанавливает мягко удалённого пользователя (устанавливает `is_active = True`).

    - **user_id**: ID пользователя (>= 0).

    **Возможные ошибки:**
    - `404 Not Found` — пользователь с указанным ID не найден.

    Доступ: admin.
    """
    try:
        return await UserService(db).restore_user(user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException