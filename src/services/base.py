from src.utils.db_manager import DBManager


class BaseService:
    """
    Базовый класс для всех сервисов приложения.

    Предоставляет унифицированный доступ к менеджеру базы данных (DBManager),
    который содержит репозитории для работы с различными сущностями (пользователи, отели и т.д.).

    Наследование от этого класса позволяет:
    - Использовать `self.db` в дочерних сервисах.
    - Поддерживать единый интерфейс взаимодействия с данными.
    - Упрощать внедрение зависимостей (DI) в FastAPI-роутах.

    Пример использования:
        class UserService(BaseService):
            async def get_user(self, user_id: int):
                return await self.db.users.get_one(id=user_id)
    """

    db: DBManager | None

    def __init__(self, db: DBManager | None = None) -> None:
        """
        Инициализирует сервис с опциональным экземпляром DBManager.

        Параметры:
        - db (DBManager | None): Менеджер базы данных. Передаётся через зависимость FastAPI.
        """
        self.db = db
