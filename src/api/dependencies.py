from typing import Annotated
from fastapi import Depends, Query, HTTPException, Request
from pydantic import BaseModel

from src.services.auth import AuthService


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


def get_token(request: Request) -> str:
    token = request.cookies.get("access_token") or None
    if not token:
        raise HTTPException(status_code=401, detail="Вы не предоставили токен доступа")
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    data = AuthService().decode_token(token)
    return data["user_id"]


UserIdDep = Annotated[int, Depends(get_current_user_id)]
