from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.repos.users import UserRepository
from src.models.users import Users
from src.schemas.users import UserWithHashedPassword, UserResponse
from src.utils.enums.user_roles import UserRoleEnum
from src.utils.exceptions.exceptions import UserNotFoundException


@pytest.fixture
def repo(mock_session):
    repo = UserRepository(mock_session)
    repo._get_query_with_params = MagicMock(return_value=select(Users))
    repo.UserWithHashedPassword = MagicMock()
    return repo

@pytest.fixture
def mock_model():
    return Users(
        id=1,
        username="test",
        hashed_password="hashed_password",
        role=UserRoleEnum.EMPLOYEE.value,
        is_active=True,
        created_at=datetime(2026, 7, 19, 12, 0)
    )
    
@pytest.fixture
def args():
    return (Users.username == "test",)

class TestGetUserWithHashedPassword:
    async def test_success(self, repo, mock_session, mock_model, args, kwargs):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_model
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_user_with_hashed_password(*args, **kwargs)
        assert isinstance(result, UserWithHashedPassword)
        mock_session.execute.assert_called_once()
    
    async def test_user_not_found(self, repo, mock_session, args, kwargs):
        mock_result = MagicMock()
        mock_result.scalar_one.side_effect = NoResultFound
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(UserNotFoundException):
            await repo.get_user_with_hashed_password(*args, **kwargs)

        mock_session.execute.assert_called_once()

class TestSoftDelete:
    async def test_success(self, repo, mock_session, mock_model):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_model
        mock_session.execute.return_value = mock_result
        
        result = await repo.soft_delete(user_id=1)
        assert isinstance(result, UserResponse)
        mock_session.execute.assert_called_once()
        
        call_args = mock_session.execute.call_args[0][0]
        compiled = call_args.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql_str = str(compiled)
        
        assert "SET is_active=false" in sql_str
    
    async def test_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one.side_effect = NoResultFound
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(UserNotFoundException):
            await repo.soft_delete(user_id=1)
        
        mock_session.execute.assert_called_once()

class TestRestore:
    async def test_success(self, repo, mock_session, mock_model):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_model
        mock_session.execute.return_value = mock_result
        
        result = await repo.restore(user_id=1)
        assert isinstance(result, UserResponse)
        mock_session.execute.assert_called_once()
        
        call_args = mock_session.execute.call_args[0][0]
        compiled = call_args.compile(
            compile_kwargs={"literal_binds": True}
        )
        sql_str = str(compiled)
        
        assert "SET is_active=true" in sql_str
    
    async def test_not_found(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one.side_effect = NoResultFound
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(UserNotFoundException):
            await repo.restore(user_id=1)
        
        mock_session.execute.assert_called_once()