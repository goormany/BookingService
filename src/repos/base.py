from asyncpg import ForeignKeyViolationError, UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import Select, select, insert, update, delete
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_mappers.base import BaseDataMapper
from src.utils.exceptions.exceptions import (
    BookingRoomsInvalidObjReferences,
    BookingRoomsNotFoundObjException,
    BookingRoomsObjUniquessException,
)


class BaseRepository:
    mapper: BaseDataMapper

    def __init__(self, session: AsyncSession):
        self.session = session

    def _get_query_with_params(self, *args, **kwargs) -> Select:
        return select(self.mapper.db_model).filter(*args).filter_by(**kwargs)

    async def get_filtred(
        self, per_page: int | None = None, page: int | None = None, *args, **kwargs
    ):
        query = self._get_query_with_params(*args, **kwargs)
        if per_page and page:
            query = (
                query.offset((page - 1) * per_page)
                .limit(per_page)
                .order_by(self.mapper.db_model.id)
            )

        result = await self.session.execute(query)
        return [self.mapper.map_to_schema(res) for res in result.scalars().all()]

    async def get_all(self, per_page: int | None, page: int | None):
        return await self.get_filtred(per_page, page)

    async def get_one(self, *args, **kwargs):
        query = self._get_query_with_params(*args, **kwargs)
        result = await self.session.execute(query)

        try:
            return self.mapper.map_to_schema(result.scalar_one())
        except NoResultFound:
            raise BookingRoomsNotFoundObjException

    async def get_one_or_none(self, *args, **kwargs):
        query = self._get_query_with_params(*args, **kwargs)
        result = await self.session.execute(query)

        item = result.scalar_one_or_none()
        if item is None:
            return None
        return self.mapper.map_to_schema(item)

    async def add(self, data: BaseModel, exclude_unset: bool = False):
        stmt = (
            insert(self.mapper.db_model)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self.mapper.db_model)
        )

        try:
            result = await self.session.execute(stmt)
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, UniqueViolationError):
                raise BookingRoomsObjUniquessException
            elif isinstance(e.orig.__cause__, ForeignKeyViolationError):
                raise BookingRoomsInvalidObjReferences
            else:
                raise e
        return self.mapper.map_to_schema(result.scalar_one())

    async def add_bulk(self, data: list[BaseModel], exclude_unset: bool = False):
        stmt = insert(self.mapper.db_model).values(
            [item.model_dump(exclude_unset=exclude_unset)] for item in data
        )

        try:
            await self.session.execute(stmt)
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, UniqueViolationError):
                raise BookingRoomsObjUniquessException
            elif isinstance(e.orig.__cause__, ForeignKeyViolationError):
                raise BookingRoomsInvalidObjReferences
            else:
                raise e

    async def edit(self, data: BaseModel, exclude_unset: bool = False, *args, **kwargs):
        stmt = (
            update(self.mapper.db_model)
            .filter(*args)
            .filter_by(**kwargs)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self.mapper.db_model)
        )

        try:
            result = await self.session.execute(stmt)
            return self.mapper.map_to_schema(result.scalar_one())
        except NoResultFound:
            raise BookingRoomsNotFoundObjException
        except IntegrityError as e:
            if isinstance(e.orig.__cause__, UniqueViolationError):
                raise BookingRoomsObjUniquessException
            else:
                raise e

    async def delete(self, *args, **kwargs):
        stmt = (
            delete(self.mapper.db_model)
            .filter(*args)
            .filter_by(**kwargs)
            .returning(self.mapper.db_model)
        )
        result = await self.session.execute(stmt)
        try:
            return self.mapper.map_to_schema(result.scalar_one())
        except NoResultFound:
            raise BookingRoomsNotFoundObjException
