from typing import Annotated

from fastapi import APIRouter, Depends, Path

from src.schemas.users import UserResponse, UserRoleSchema
from src.services.users import UserService
from src.api.dependencies.db import DBDep
from src.api.dependencies.users import CurUserDep, get_admin_user
from src.utils.enums.user_roles import UserRoleEnum
from src.utils.exceptions.exceptions import UserNotFoundException
from src.utils.exceptions.http_exceptions import UserNotFoundHTTPException

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse], status_code=200, dependencies=[Depends(get_admin_user)])
async def get_all_users(db: DBDep):
    return await UserService(db).get_all()

@router.get("/me", response_model=UserResponse, status_code=200)
async def get_user_me(user_data: CurUserDep):
    return user_data

@router.get("/{user_id}", response_model=UserResponse, status_code=200, dependencies=[Depends(get_admin_user)])
async def get_user_by_id(db: DBDep, user_id: Annotated[int, Path(ge=0)]):
    try:
        return await UserService(db).get_user(id=user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException

@router.patch("/{user_id}", status_code=200, response_model=UserResponse, dependencies=[Depends(get_admin_user)])
async def change_user_role(db: DBDep, user_id: Annotated[int, Path(ge=0)], role: UserRoleSchema):
    try:
        return await UserService(db).change_user_role(user_id, role)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    
@router.delete("/{user_id}", response_model=UserResponse, status_code=200, dependencies=[Depends(get_admin_user)])
async def soft_delete_user(db: DBDep, user_id: Annotated[int, Path(ge=0)]):
    try:
        return await UserService(db).soft_delete(user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException

@router.delete("/{user_id}/hard", response_model=UserResponse, status_code=200, dependencies=[Depends(get_admin_user)])
async def hard_delete_user(db: DBDep, user_id: Annotated[int, Path(ge=0)]):
    try:
        return await UserService(db).hard_delete(user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException

@router.patch("/{user_id}/restore", status_code=200, response_model=UserResponse, dependencies=[Depends(get_admin_user)])
async def restore_user(db: DBDep, user_id: Annotated[int, Path(ge=0)]):
    try:
        return await UserService(db).restore_user(user_id)
    except UserNotFoundException:
        raise UserNotFoundHTTPException