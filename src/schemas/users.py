from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.validators import NonEmptyStr
from src.utils.enums.user_roles import UserRoleEnum


class UserBase(BaseModel):
    username: NonEmptyStr = Field(min_length=4)


class UserIn(UserBase):
    password: NonEmptyStr = Field(min_length=4)


class UserResponse(UserBase):
    id: int
    role: UserRoleEnum
    created_at: datetime
    is_active: bool


class UserCreate(BaseModel):
    username: NonEmptyStr
    hashed_password: str
    role: UserRoleEnum = UserRoleEnum.EMPLOYEE


class UserWithHashedPassword(UserResponse):
    hashed_password: str


class UserRoleSchema(BaseModel):
    role: UserRoleEnum
