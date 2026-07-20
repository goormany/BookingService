from unittest.mock import MagicMock

import pytest

from src.repos.health import HealthRepository
from src.utils.exceptions.exceptions import BookingNotConnDBException


@pytest.fixture
def repo(mock_session):
    repo = HealthRepository(mock_session)
    return repo


class TestCheckConnectDB:
    async def test_success(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1

        mock_session.execute.return_value = mock_result

        result = await repo.check_connect_db()

        assert isinstance(result, int)
        assert result == 1
        mock_session.execute.assert_called_once()

    async def test_not_connected_db(self, repo, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one.side_effect = ConnectionRefusedError

        mock_session.execute.return_value = mock_result

        with pytest.raises(BookingNotConnDBException):
            await repo.check_connect_db()

        mock_session.execute.assert_called_once()
