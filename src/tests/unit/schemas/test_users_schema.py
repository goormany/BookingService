from pydantic import ValidationError
import pytest

from src.schemas.users import UserIn, UserRoleSchema, UserCreate
from src.utils.enums.user_roles import UserRoleEnum

class TestUserIn:
    def test_valid(self):
        schema = UserIn(username="john", password="secret123")
        assert schema.username == "john"
        assert schema.password == "secret123"

    @pytest.mark.parametrize("value", ["", "   "])
    def test_invalid_empty_username(self, value):
        with pytest.raises(ValidationError):
            UserIn(username=value, password="secret123")

    @pytest.mark.parametrize("value", ["", "   "])
    def test_invalid_empty_password(self, value):
        with pytest.raises(ValidationError):
            UserIn(username="john", password=value)

class TestUserCreate:
    def test_valid(self):
        schema = UserCreate(username="john", hashed_password="hash123")
        assert schema.username == "john"
        assert schema.role == UserRoleEnum.EMPLOYEE

    def test_empty_username(self):
        with pytest.raises(ValidationError):
            UserCreate(username="", hashed_password="hash123")

class TestUserRoleSchema:
    def test_valid_role_admin(self):
        schema = UserRoleSchema(role="admin")
        assert schema.role == UserRoleEnum.ADMIN

    def test_valid_role_employee(self):
        schema = UserRoleSchema(role="employee")
        assert schema.role == UserRoleEnum.EMPLOYEE

    @pytest.mark.parametrize("invalid_role", ["user", "manager", "superadmin", ""])
    def test_invalid_role(self, invalid_role):
        with pytest.raises(ValidationError):
            UserRoleSchema(role=invalid_role)
