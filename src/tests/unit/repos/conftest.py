from unittest.mock import create_autospec

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_session() -> AsyncSession:
    mock_session = create_autospec(AsyncSession)
    return mock_session


@pytest.fixture
def kwargs():
    return {"id": 1}
