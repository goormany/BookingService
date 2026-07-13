from typing import TypeVar

from pydantic import BaseModel

from src.db.database import Base

DBModelType = TypeVar('DBModelType', bound=Base)
SchemaType = TypeVar('SchemaType', bound=BaseModel)

class BaseDataMapper:
    db_model: DBModelType | None = None
    schema: SchemaType | None = None
    
    @classmethod
    def map_to_schema(cls, data: DBModelType) -> SchemaType:
        return cls.schema.model_validate(data, from_attributes=True)
    
    @classmethod
    def map_to_db_model(cls, data: SchemaType) -> DBModelType:
        return cls.db_model(**data.model_dump())