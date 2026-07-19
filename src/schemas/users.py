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
    is_active: bool

class UserCreate(UserBase):
    hashed_password: str
    role: UserRoleEnum = UserRoleEnum.EMPLOYEE
    

class UserWithHashedPassword(UserResponse, UserCreate):
    pass

class UserRoleSchema(BaseModel):
    role: UserRoleEnum