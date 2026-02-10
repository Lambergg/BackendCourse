from src.schemas.facilities import FacilitiesAdd
from src.services.base import BaseService
from src.tasks.tasks import test_task


class FacilityService(BaseService):
    """
    Сервис для управления удобствами (facilities).

    Предоставляет методы:
    - Создание нового удобства.
    - Получение списка всех удобств.

    Наследуется от `BaseService`, имеет доступ к `self.db` (DBManager).
    """

    async def create_facility(self, data: FacilitiesAdd):
        """
        Добавляет новое удобство в систему.

        Параметры:
        - data (FacilitiesAdd): Данные для создания удобства — название.

        Логика:
        1. Передаёт данные в репозиторий `facilities.add()`.
        2. Фиксирует транзакцию.
        3. Запускает фоновую задачу Celery (test_task).

        Фоновая задача:
        - Используется для демонстрации интеграции с Celery.
        - Может быть заменена на реальную логику (например, уведомления, логирование и т.д.).

        Возвращает:
        - Созданное удобство как Pydantic-схему.
        """
        facilities = await self.db.facilities.add(data)
        await self.db.commit()

        test_task.delay()  # type: ignore
        return facilities

    async def get_facilities(self):
        """
        Возвращает список всех удобств.

        Логика:
        - Вызывает `self.db.facilities.get_all()`.

        Возвращает:
        - Список Pydantic-схем `Facilities`.
        """
        return await self.db.facilities.get_all()
