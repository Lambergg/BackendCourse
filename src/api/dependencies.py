from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(None, ge=1, description="Текущая страница")]
    per_page: Annotated[int | None, Query(None, ge=1, ls=30, description="Элементов на странице")]


PaginationDep = Annotated[PaginationParams, Depends()]
