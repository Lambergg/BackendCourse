from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    """
    Схема параметров пагинации для HTTP-запросов.

    Используется для валидации и получения параметров пагинации из query-строки
    входящего запроса. Позволяет контролировать постраничный вывод данных.

    Attributes:
        page (int | None): Номер текущей страницы. Должен быть целым числом не меньше 1.
                          По умолчанию — 1 (первая страница).
        per_page (int | None): Количество элементов на одной странице. Должен быть целым
                               числом в диапазоне от 1 до 30. Если не указан, значение
                               определяется логикой приложения.
    """
    page: Annotated[int | None, Query(1, ge=1, description="Текущая страница")]
    per_page: Annotated[int | None, Query(None, ge=1, ls=30, description="Элементов на странице")]


PaginationDep = Annotated[PaginationParams, Depends()]
"""
Зависимость FastAPI для внедрения параметров пагинации в эндпоинты.

Используется как тип-зависимость в параметрах маршрутов FastAPI для автоматического
получения, валидации и внедрения объекта PaginationParams из query-параметров запроса.

Example:
    @router.get("/items")
    async def get_items(pagination: PaginationDep):
        return paginate(items, pagination.page, pagination.per_page)
"""
