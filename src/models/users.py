from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.db.database import Base
from src.utils.enums.user_roles import UserRoleEnum


class Users(Base):
    username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
    hashed_password: Mapped[str]
    role: Mapped[UserRoleEnum] = mapped_column(default=UserRoleEnum.EMPLOYEE.value)