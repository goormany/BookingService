from datetime import datetime

from pydantic import BaseModel

from src.utils.enums.user_roles import UserRoleEnum

class UserBase(BaseModel):
    username: str

class UserIn(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRoleEnum
    created_at: datetime

class UserWithHashedPassword(UserResponse):
    hashed_password: str