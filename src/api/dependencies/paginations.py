from typing import Annotated

from pydantic import BaseModel
from fastapi import Depends, Query


class PaginationParams(BaseModel):
    page: int = Query(ge=1, default=1)
    per_page: int = Query(ge=1, default=20, le=20)


PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]
