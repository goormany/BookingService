from asyncpg import ForeignKeyViolationError, UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.data_mappers.base import BaseDataMapper
from src.utils.exceptions.exceptions import BookingRoomsInvalidObjReferences, BookingRoomsNotFoundObjException, BookingRoomsObjUniquessException

class BaseRepository:
    mapper: BaseDataMapper
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    def _get_query_with_params(self, *args, **kwargs):
        return select(self.mapper.db_model).filter(*args).filter_by(**kwargs)
    
    async def get_filtred(self, *args, **kwargs):
        query = self._get_query_with_params(*args, **kwargs)
        result = await self.session.execute(query)
        return [self.mapper.map_to_schema(res) for res in result.scalars().all()]
    
    async def get_all(self):
        return await self.get_filtred()
    
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
        stmt = (
            insert(self.mapper.db_model)
            .values([item.model_dump(exclude_unset=exclude_unset)] for item in data)
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
        
        result = await self.session.execute(stmt)
        try:
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
            return self.mapper.map_to_db_model(result.scalar_one())
        except NoResultFound:
            raise BookingRoomsNotFoundObjException
