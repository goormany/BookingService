from typing import Annotated

from fastapi import Depends

from src.api.dependencies.auth import tokenDep
from src.api.dependencies.db import DBDep
from src.schemas.users import UserResponse
from src.services.auth import AuthServices
from src.services.users import UserService
from src.utils.exceptions.exceptions import ExpiredJWTTokenException, InvalidTokenDecodedException, UserNotFoundException
from src.utils.exceptions.http_exceptions import ForbbidenHTTPException, UnauthorizedHTTPException, UserSoftDeleteAccountException
from src.utils.enums.user_roles import UserRoleEnum

async def get_current_user(db:DBDep, token: tokenDep) -> UserResponse:
    try:
        jwt_data = AuthServices.decode_access_token(token)
    except (InvalidTokenDecodedException, ExpiredJWTTokenException):
        raise UnauthorizedHTTPException
    user_id = int(jwt_data.sub)
    
    try:
        user = await UserService(db).get_user(id=user_id)
    except UserNotFoundException:
        raise UnauthorizedHTTPException
    
    if not user.is_active:
        raise UserSoftDeleteAccountException
    
    return user

CurUserDep = Annotated[UserResponse, Depends(get_current_user)]

async def get_employee_user(user: CurUserDep):
    if user.role not in (UserRoleEnum.EMPLOYEE.value, UserRoleEnum.ADMIN.value):
        raise ForbbidenHTTPException
    return user

async def get_admin_user(user: CurUserDep):
    if user.role != UserRoleEnum.ADMIN.value:
        raise ForbbidenHTTPException
    return user

EmployeeDep = Annotated[UserResponse, Depends(get_employee_user)]
AdminDep = Annotated[UserResponse, Depends(get_admin_user)]
