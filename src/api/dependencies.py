from typing import Annotated
from fastapi import Depends, Query, HTTPException, Request
from pydantic import BaseModel

from src.database import async_session_maker
from src.services.auth import AuthService
from src.utils.db_manager import DBManager


class PaginationParams(BaseModel):
    """
    Параметры для пагинации в GET-запросах.

    Используется как зависимость через `PaginationDep`.

    Поля:
    - page: Номер страницы (начиная с 1)
    - per_page: Количество элементов на странице (максимум 30)
    """

    page: Annotated[int, Query(1, ge=1, description="Текущая страница")]
    per_page: Annotated[int | None, Query(None, ge=1, le=30, description="Элементов на странице")]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    """
    Извлекает JWT-токен из куки `access_token`.

    Параметры:
    - request (Request): Объект HTTP-запроса.

    Логика:
    - Пытается получить `access_token` из кук.
    - Если токена нет — выбрасывает 401 Unauthorized.

    Возвращает:
    - Токен в виде строки.
    """
    token = request.cookies.get("access_token") or None
    if not token:
        raise HTTPException(status_code=401, detail="Вы не предоставили токен доступа")
    return token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    """
    Декодирует JWT-токен и возвращает ID пользователя.

    Параметры:
    - token (str): Токен, полученный через `get_token`.

    Логика:
    - Вызывает `AuthService.decode_token()` для декодирования.
    - Извлекает `user_id` из payload (`sub`).
    - Если токен невалиден или просрочен — выбрасывается ошибка в `decode_token`.

    Возвращает:
    - ID пользователя (int).
    """
    data = AuthService().decode_token(token)
    return data["user_id"]


UserIdDep = Annotated[int, Depends(get_current_user_id)]


def get_db_manager():
    """
    Фабрика для создания экземпляра DBManager.

    Возвращает:
    - Новый экземпляр DBManager с фабрикой сессий.
    """
    return DBManager(session_factory=async_session_maker)


async def get_db():
    """
    Асинхронная зависимость для работы с базой данных.

    Создаёт менеджер БД и предоставляет его через `yield`.
    Автоматически закрывает сессию после завершения запроса.

    Используется как зависимость через `DBDep`.

    Возвращает:
    - Экземпляр DBManager.
    """
    async with get_db_manager() as db:
        yield db


DBDep = Annotated[DBManager, Depends(get_db)]
