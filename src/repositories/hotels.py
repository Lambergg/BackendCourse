from datetime import date

from sqlalchemy import select, func

from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.models.hotels import HotelsOrm
from src.repositories.mappers.mappers import HotelDataMapper
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    """
    Репозиторий для работы с отелями.

    Предоставляет методы для получения отелей с фильтрацией по:
    - Доступности номеров в указанный период.
    - Локации.
    - Названию.
    - Пагинации (limit/offset).

    Атрибуты:
    - model: ORM-модель `HotelsOrm`.
    - mapper: Маппер `HotelDataMapper` для преобразования в Pydantic-схему.
    """
    model = HotelsOrm
    mapper = HotelDataMapper

    async def get_filtered_by_time(
        self,
        date_from: date,
        date_to: date,
        location,
        title,
        limit,
        offset,
    ) -> list[Hotel]:
        """
        Возвращает список отелей, у которых есть доступные номера в указанный период.

        Параметры:
        - date_from (date): Дата заезда.
        - date_to (date): Дата выезда.
        - location (str | None): Фильтр по местоположению (поиск подстроки, без учёта регистра).
        - title (str | None): Фильтр по названию отеля (поиск подстроки, без учёта регистра).
        - limit (int): Максимальное количество результатов.
        - offset (int): Смещение для пагинации.

        Логика:
        1. Использует CTE-запрос `rooms_ids_for_booking()` для получения ID доступных номеров.
        2. Получает ID отелей, которым принадлежат эти номера.
        3. Выполняет `SELECT` отелей с фильтрацией по `location` и `title`.
        4. Применяет `LIMIT` и `OFFSET`.

        Особенности:
        - Поиск по `location` и `title` — через `ILIKE` (через `func.lower().contains()`).
        - Чувствителен к регистру → приводится к нижнему.

        Возвращает:
        - Список Pydantic-схем `Hotel`, соответствующих условиям.
        """
        # Получаем ID номеров, доступных в указанный период
        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)

        # Получаем ID отелей, где есть такие номера
        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        # Строим основной запрос на выборку отелей
        query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids_to_get))

        # Добавляем фильтр по местоположению
        if location:
            query = query.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))

        # Добавляем фильтр по названию
        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))

        # Пагинация
        query = query.limit(limit).offset(offset)

        # Логирование SQL (для отладки — раскомментировать при необходимости)
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(hotel) for hotel in result.scalars().all()]
