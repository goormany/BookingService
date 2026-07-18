from pydantic import ValidationError
import pytest

from src.schemas.users import UserRoleSchema
from src.utils.enums.user_roles import UserRoleEnum

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