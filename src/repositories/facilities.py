from typing import Sequence
from sqlalchemy import select, delete, insert

from src.repositories.base import BaseRepository
from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.repositories.mappers.mappers import FacilityDataMapper
from src.schemas.facilities import RoomsFacilities


class FacilitiesRepository(BaseRepository):
    """
    Репозиторий для работы с удобствами (facilities).

    Предоставляет стандартные CRUD-операции через BaseRepository.

    Атрибуты:
    - model: ORM-модель `FacilitiesOrm`.
    - mapper: Маппер `FacilityDataMapper` для преобразования в Pydantic-схему.
    """
    model = FacilitiesOrm
    mapper = FacilityDataMapper

    async def get_many_by_ids(self, ids: list[int]) -> list[FacilitiesOrm]:
        """
        Возвращает список удобств по списку ID.
        Только существующие.
        """
        query = select(self.model).where(self.model.id.in_(ids))
        result = await self.session.execute(query)
        return list(result.scalars().all())


class RoomsFacilitiesRepository(BaseRepository):
    """
    Репозиторий для работы с ассоциативной таблицей `rooms_facilities`.

    Управляет связями "многие ко многим" между номерами и удобствами.

    Атрибуты:
    - model: ORM-модель `RoomsFacilitiesOrm`.
    - schema: Pydantic-схема `RoomsFacilities` (используется напрямую без маппера).
    """
    model: RoomsFacilitiesOrm = RoomsFacilitiesOrm
    schema = RoomsFacilities

    async def set_room_facilities(self, room_id: int, facilities_ids: list[int]) -> None:
        """
        Настраивает удобства для указанного номера.

        Сравнивает текущие удобства номера с новыми и:
        - Удаляет связи для исключённых удобств.
        - Добавляет связи для новых удобств.

        Параметры:
        - room_id (int): ID номера.
        - facilities_ids (list[int]): Список ID удобств, которые должны быть у номера.

        Логика:
        1. Получает текущие `facility_id` из таблицы `rooms_facilities` для `room_id`.
        2. Находит разницу:
            - `ids_to_delete`: есть сейчас, но нет в новых.
            - `ids_to_insert`: нет сейчас, но есть в новых.
        3. Выполняет `DELETE` и `INSERT` при необходимости.

        Пример:
            await repo.set_room_facilities(1, [1, 2, 5])
            # Удалит связи с удобствами, кроме 1,2,5
            # Добавит связи с 1,2,5 (если их не было)
        """
        # Получаем текущие ID удобств номера
        get_current_facilities_ids_query = select(self.model.facility_id).filter_by(room_id=room_id)
        res = await self.session.execute(get_current_facilities_ids_query)
        current_facilities_ids: Sequence[int] = res.scalars().all()
        # Определяем, что удалять и что добавлять
        ids_to_delete: list[int] = list(set(current_facilities_ids) - set(facilities_ids))
        ids_to_insert: list[int] = list(set(facilities_ids) - set(current_facilities_ids))

        # Удаляем лишние связи
        if ids_to_delete:
            delete_m2m_facilities_stmt = delete(self.model).filter(  # type: ignore
                self.model.room_id == room_id,  # type: ignore
                self.model.facility_id.in_(ids_to_delete),  # type: ignore
            )
            await self.session.execute(delete_m2m_facilities_stmt)

        # Добавляем новые связи
        if ids_to_insert:
            insert_m2m_facilities_stmt = insert(self.model).values(  # type: ignore
                [{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_insert]
            )
            await self.session.execute(insert_m2m_facilities_stmt)
