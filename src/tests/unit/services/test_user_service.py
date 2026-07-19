from unittest.mock import AsyncMock, patch

import pytest

from src.schemas.users import UserIn, UserRoleSchema
from src.services.auth import AuthServices
from src.services.users import UserService
from src.models.users import Users
from src.utils.enums.user_roles import UserRoleEnum
from src.utils.exceptions.exceptions import BookingRoomsNotFoundObjException, BookingRoomsObjUniquessException, UserNotFoundException, UsersUniquessException


@pytest.fixture
def service():
    db = AsyncMock()
    db.users = AsyncMock()
    return UserService(db)

@pytest.fixture
def user_in():
    return UserIn(
        username="test",
        password="test_password"
    )
    
@pytest.fixture
def mock_hashed_password():
    return "hashed"

@pytest.fixture
def args():
    return (Users.username == "test",)

@pytest.fixture
def kwargs():
    return {"id": 1}

class TestCreateUser:
    async def test_success(self, service, user_in, mock_hashed_password):
        with patch.object(AuthServices, "get_password_hash", return_value=mock_hashed_password):
            service.db.users.add.return_value = "user_response"
            
            result = await service.create_user(user_in)
            
            service.db.users.add.assert_called_once()
            service.db.commit.assert_called_once()
            
            assert isinstance(result, str)
            assert result == "user_response"
    
    async def test_uniques_error(self, service, user_in, mock_hashed_password):
        with patch.object(AuthServices, "get_password_hash", return_value=mock_hashed_password):
            service.db.users.add.side_effect = BookingRoomsObjUniquessException()
            
            with pytest.raises(UsersUniquessException):
                await service.create_user(user_in)
            
            service.db.users.add.assert_called_once()
            service.db.commit.assert_not_called()

class TestGetUserWithPassword:
    async def test_success(self, service, args, kwargs):
        service.db.users.get_user_with_hashed_password.return_value = "user_with_hashed_password"
        
        result = await service.get_user_with_password(*args, **kwargs)
        
        assert isinstance(result, str)
        assert result == "user_with_hashed_password"
        
        service.db.users.get_user_with_hashed_password.assert_called_once_with(*args, **kwargs)

    async def test_not_found_user(self, service, args, kwargs):
        service.db.users.get_user_with_hashed_password.side_effect = UserNotFoundException
        
        with pytest.raises(UserNotFoundException):
            await service.get_user_with_password(*args, **kwargs)
        
        service.db.users.get_user_with_hashed_password.assert_called_once_with(*args, **kwargs)

class TestGetUser:
    async def test_success(self, service, args, kwargs):
        service.db.users.get_one.return_value = "user_response"
        
        result = await service.get_user(*args, **kwargs)
        
        assert isinstance(result, str)
        assert result == "user_response"
        
        service.db.users.get_one.assert_called_once_with(*args, **kwargs)

    async def test_user_not_found(self, service, args, kwargs):
        service.db.users.get_one.side_effect = BookingRoomsNotFoundObjException()
        
        with pytest.raises(UserNotFoundException):
            await service.get_user(*args, **kwargs)
        
        service.db.users.get_one.assert_called_once_with(*args, **kwargs)

class TestGetAll:
    async def test_without_pagination(self, service):
        service.db.users.get_all.return_value = ["user1", "user2"]
        
        page = None
        per_page = None
        
        result = await service.get_all(per_page=per_page, page=page)
        assert isinstance(result, list)
        assert result == ["user1", "user2"]
        assert result[0] == "user1"
        assert result[1] == "user2"
        
        service.db.users.get_all.assert_called_once()
        
        call_args = service.db.users.get_all.call_args
        assert call_args.kwargs["per_page"] is None
        assert call_args.kwargs["page"] is None

    async def test_with_pagination(self, service):
        service.db.users.get_all.return_value = ["user1", "user2"]
        
        page = 5
        per_page = 3
        
        result = await service.get_all(per_page=per_page, page=page)
        assert isinstance(result, list)
        assert result == ["user1", "user2"]
        assert result[0] == "user1"
        assert result[1] == "user2"
        
        service.db.users.get_all.assert_called_once()
        
        call_args = service.db.users.get_all.call_args
        assert call_args.kwargs["per_page"] == per_page
        assert call_args.kwargs["page"] == page

class TestChangeUserRole:
    @pytest.mark.parametrize("role", [UserRoleEnum.ADMIN, UserRoleEnum.EMPLOYEE])
    async def test_success(self, service, role):
        service.db.users.edit.return_value = "new_user"
        user_id = 1
        
        result = await service.change_user_role(user_id=user_id, role=UserRoleSchema(role=role))
        
        assert isinstance(result, str)
        assert result == "new_user"
        
        service.db.users.edit.assert_called_once()
        service.db.commit.assert_called_once()

    @pytest.mark.parametrize("role", [UserRoleEnum.ADMIN, UserRoleEnum.EMPLOYEE])
    async def test_not_found_user(self, service, role):
        service.db.users.edit.side_effect = BookingRoomsNotFoundObjException()
        user_id = 1
        
        with pytest.raises(UserNotFoundException):
            await service.change_user_role(user_id=user_id, role=UserRoleSchema(role=role))
        
        service.db.users.edit.assert_called_once()
        service.db.commit.assert_not_called()

class TestSoftDelete:
    async def test_success(self, service):
        service.db.users.soft_delete.return_value = "del_user"
        user_id = 1
        
        result = await service.soft_delete(user_id=user_id)
        
        assert isinstance(result, str)
        assert result == "del_user"
        
        service.db.users.soft_delete.assert_called_once_with(user_id)
        service.db.commit.assert_called_once()

    async def test_user_not_found(self, service):
        service.db.users.soft_delete.side_effect = BookingRoomsNotFoundObjException()
        user_id = 1
        
        with pytest.raises(UserNotFoundException):
            await service.soft_delete(user_id=user_id)
        
        service.db.users.soft_delete.assert_called_once_with(user_id)
        service.db.commit.assert_not_called()

class TestHardDelete:
    async def test_success(self, service):
        service.db.users.delete.return_value = "del_user"
        user_id = 1
        
        result = await service.hard_delete(user_id=user_id)
        
        assert isinstance(result, str)
        assert result == "del_user"
        
        service.db.users.delete.assert_called_once_with(id=user_id)
        service.db.commit.assert_called_once()

    async def test_user_not_found(self, service):
        service.db.users.delete.side_effect = BookingRoomsNotFoundObjException()
        user_id = 1
        
        with pytest.raises(UserNotFoundException):
            await service.hard_delete(user_id=user_id)
        
        service.db.users.delete.assert_called_once_with(id=user_id)
        service.db.commit.assert_not_called()

class TestRestoreUser:
    async def test_success(self, service):
        service.db.users.restore.return_value = "del_user"
        user_id = 1
        
        result = await service.restore_user(user_id=user_id)
        
        assert isinstance(result, str)
        assert result == "del_user"
        
        service.db.users.restore.assert_called_once_with(user_id)
        service.db.commit.assert_called_once()

    async def test_user_not_found(self, service):
        service.db.users.restore.side_effect = BookingRoomsNotFoundObjException()
        user_id = 1
        
        with pytest.raises(UserNotFoundException):
            await service.restore_user(user_id=user_id)
        
        service.db.users.restore.assert_called_once_with(user_id)
        service.db.commit.assert_not_called()