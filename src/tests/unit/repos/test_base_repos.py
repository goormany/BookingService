from unittest.mock import AsyncMock, MagicMock, create_autospec

from asyncpg import ForeignKeyViolationError, UniqueViolationError
from pydantic import BaseModel
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.repos.base import BaseRepository
from src.utils.exceptions.exceptions import BookingRoomsInvalidObjReferences, BookingRoomsNotFoundObjException, BookingRoomsObjUniquessException

class TestBase(DeclarativeBase):
    pass

class TestModel(TestBase):
    __tablename__ = "tests"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(nullable=True)
    
    def __str__(self):
        return f"test_model_{self.id}"

class TestSchema(BaseModel):
    id: int
    name: str | None = None

class TestDataMapper:
    db_model = TestModel
    schema = TestSchema
    
    @classmethod
    def map_to_schema(cls, obj):
        return f"map_{obj}"

@pytest.fixture
def repo(mock_session) -> BaseRepository:
    repo = BaseRepository(mock_session)
    repo.mapper = TestDataMapper
    repo._get_query_with_params = MagicMock(return_value=select(TestModel))
    return repo

@pytest.fixture
def mock_model():
    return TestModel(id=1, name="test_name")

@pytest.fixture
def mock_schema():
    return TestSchema(id=1, name=None)

@pytest.fixture
def args():
    return (TestModel.name == "test_name",)

class TestGetFiltred:
    async def test_get_filtred_without_pagination(self, repo: BaseRepository, mock_session: AsyncSession):
        mock_models = [TestModel(id=1), TestModel(id=2, name="test2")]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_models
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_filtred()
        
        assert len(result) == 2
        assert result[0] == "map_test_model_1"
        assert result[1] == "map_test_model_2"
        
        mock_session.execute.assert_called_once()
        
        call_args = mock_session.execute.call_args[0][0]
        
        assert call_args._offset is None
        assert call_args._limit is None
        
    async def test_get_filtred_with_pagination(self, repo, mock_session):
        mock_models = [TestModel(id=1)]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_models
        
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        mock_session.execute.return_value = mock_result
        
        page = 1
        per_page = 5
        
        result = await repo.get_filtred(page=page, per_page=per_page)
        
        assert len(result) == 1
        assert result[0] == "map_test_model_1"
        mock_session.execute.assert_called_once()
        
        call_args = mock_session.execute.call_args[0][0]
        assert call_args._limit is not None and call_args._limit == per_page
        assert call_args._offset is not None and call_args._offset == (page - 1)*per_page

class TestGetAll:
    @pytest.mark.parametrize(
        "page, per_page",
        [
            (None, None),
            (1, 5),
            (2, 5)
        ]
    )
    async def test_get_all(self, repo, page, per_page):
        repo.get_filtred = AsyncMock(return_value=[1, 2])
        
        result = await repo.get_all(page=page, per_page=per_page)
        
        assert len(result) == 2
        assert result[0] == 1
        assert result[1] == 2
        
        assert result == [1, 2]
        
        repo.get_filtred.assert_called_once_with(per_page, page)

class TestGetOne:
    
    @pytest.fixture
    def setup_mock_session(self, mock_session, mock_model):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_model
        mock_session.execute.return_value = mock_result
        return mock_session
    
    async def test_get_one_success(self, repo, setup_mock_session, args, kwargs):
        result = await repo.get_one(*args, **kwargs)
        
        repo._get_query_with_params.assert_called_once_with(*args, **kwargs)
        
        setup_mock_session.execute.assert_called_once()
        setup_mock_session.execute.return_value.scalar_one.assert_called_once()
        
        assert result == "map_test_model_1"
    
    async def test_get_onr_no_result_found(self, repo, mock_session, args, kwargs):
        mock_result = MagicMock()
        mock_result.scalar_one.side_effect = NoResultFound()
        
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(BookingRoomsNotFoundObjException):
            await repo.get_one(*args, **kwargs)
        
        repo._get_query_with_params.assert_called_once_with(*args, **kwargs)
        mock_session.execute.assert_called_once()

class TestGetOneOrNone:
    async def test_get_one_or_none_ret_not_none(self, repo, mock_session, mock_model, args, kwargs):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_model
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_one_or_none(*args, **kwargs)
        
        assert result is not None
        assert isinstance(result, str)
        assert result == "map_test_model_1"
        
        repo._get_query_with_params.assert_called_once_with(*args, **kwargs)
        mock_session.execute.assert_called_once()
    
    async def test_get_one_or_none_ret_none(self, repo, mock_session, args, kwargs):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.get_one_or_none(*args, **kwargs)
        
        assert result is None
        
        repo._get_query_with_params.assert_called_once_with(*args, **kwargs)
        mock_session.execute.assert_called_once()

class TestAdd:
    async def test_add_success(self, repo, mock_session, mock_model, mock_schema):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_model
        
        mock_session.execute.return_value = mock_result
        
        result = await repo.add(mock_schema)
        
        assert result is not None
        assert isinstance(result, str)
        assert result == "map_test_model_1"
        
        mock_session.execute.assert_called_once()
    
    async def test_add_raises_unique_violation(self, repo, mock_session, mock_schema):
        mock_unique_error = MagicMock()
        mock_unique_error.__cause__ = MagicMock(spec=UniqueViolationError)

        integrity_error = IntegrityError(
            statement="stmt",
            params={},
            orig=mock_unique_error
        )
        integrity_error.orig = mock_unique_error
        
        mock_session.execute.side_effect = integrity_error
        
        with pytest.raises(BookingRoomsObjUniquessException):
            await repo.add(mock_schema)

        mock_session.execute.assert_called_once()
    
    async def test_add_raises_foreig_key_violation(self, repo, mock_session, mock_schema):
        mock_error = MagicMock()
        mock_error.__cause__ = MagicMock(spec=ForeignKeyViolationError)
        
        integrity_error = IntegrityError(
            statement="stmt",
            params={},
            orig=mock_error
        )
        integrity_error.orig = mock_error
        
        mock_session.execute.side_effect = integrity_error
        
        with pytest.raises(BookingRoomsInvalidObjReferences):
            await repo.add(mock_schema)

class TestEdit:
    async def test_edit_success(self, repo, mock_session, mock_model, mock_schema):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_model
        mock_session.execute.return_value = mock_result
        
        result = await repo.edit(mock_schema)
        
        assert isinstance(result, str)
        assert result == "map_test_model_1"
        mock_session.execute.assert_called_once()
    
    async def test_edit_raises_not_found(self, repo, mock_session, mock_schema):
        mock_result = MagicMock()
        mock_result.scalar_one.side_effect = NoResultFound()
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(BookingRoomsNotFoundObjException):
            await repo.edit(mock_schema)
        
        mock_session.execute.assert_called_once()
    
    async def test_edit_raises_unique_violation(self, repo, mock_session, mock_schema):
        mock_error = MagicMock()
        mock_error.__cause__ = MagicMock(spec=UniqueViolationError)
        
        integrity_error = IntegrityError(
            statement="stmt",
            params={},
            orig=mock_error
        )
        integrity_error.orig = mock_error
        
        mock_session.execute.side_effect = integrity_error
        
        with pytest.raises(BookingRoomsObjUniquessException):
            await repo.edit(mock_schema)
    
class TestDelete:
    async def test_delete_success(self, repo, mock_session, mock_model, args, kwargs):
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = mock_model
        mock_session.execute.return_value = mock_result
        
        result = await repo.delete(*args, **kwargs)
        assert isinstance(result, str)
        assert result == "map_test_model_1"
        mock_session.execute.assert_called_once()

    async def test_delete_raise_not_found(self, repo, mock_session, args, kwargs):
        mock_result = MagicMock()
        mock_result.scalar_one.side_effect = NoResultFound
        mock_session.execute.return_value = mock_result
        
        with pytest.raises(BookingRoomsNotFoundObjException):
            await repo.delete(*args, **kwargs)
        
        mock_session.execute.assert_called_once()