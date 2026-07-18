from src.utils.enums.status_bookings import StatusBookingEnum
from src.utils.enums.user_roles import UserRoleEnum

class TestStatusBookingEnum:
    def test_values(self):
        assert StatusBookingEnum.ACTIVE.value == "active"
        assert StatusBookingEnum.CANCELLED.value == "cancelled"
    
    def test_count(self):
        assert len(StatusBookingEnum) == 2

class TestUserRoleEnum:
    def test_value(self):
        assert UserRoleEnum.ADMIN.value == "admin"
        assert UserRoleEnum.EMPLOYEE.value == "employee"
    
    def test_count(self):
        assert len(UserRoleEnum) == 2