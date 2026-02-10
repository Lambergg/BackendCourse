from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from src.exceptions import RoomNotFoundException
from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.repositories.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper
from src.repositories.utils import rooms_ids_for_booking


class RoomsRepository(BaseRepository):
    """
    Репозиторий для работы с номерами отелей.

    Предоставляет методы:
    - Получение номеров с фильтрацией по доступности в указанный период.
    - Получение одного номера с удобствами (lazy loading через `selectinload`).

    Атрибуты:
    - model: ORM-модель `RoomsOrm`.
    - mapper: Маппер `RoomDataMapper` (по умолчанию).
    """

    model: RoomsOrm = RoomsOrm
    mapper = RoomDataMapper

    async def get_filtered_by_time(self, hotel_id: int, date_from: date, date_to: date):
        """
        Возвращает список доступных номеров в указанном отеле и периоде.

        Использует CTE-запрос (через `rooms_ids_for_booking`) для определения,
        какие номера **не полностью забронированы** в заданный интервал.

        Параметры:
        - hotel_id (int): ID отеля.
        - date_from (date): Дата заезда.
        - date_to (date): Дата выезда.

        Логика:
        1. Выполняет CTE-подзапрос `rooms_ids_for_booking()` → получает ID свободных номеров.
        2. Формирует основной запрос:
           - Загружает номера по этим ID.
           - Использует `selectinload` для предварительной загрузки связанных удобств (`facilities`).
        3. Преобразует результаты через `RoomDataWithRelsMapper`.
        -- CTE общее табличное выражение
            with rooms_count as (
                select room_id, count(*) as rooms_reserved from bookings
                where date_from <= '2025-12-31' and date_to >= '2025-12-29'
                group by room_id
            ),
            rooms_left_result as (
                select rooms.id as room_id, quantity - coalesce(rooms_reserved, 0) as rooms_left
                from rooms
                left join rooms_count on rooms.id = rooms_count.room_id
            )
            select * from rooms_left_result
            where rooms_left > 0
            ;
        Возвращает:
        - Список Pydantic-схем `RoomWithRels`, содержащих данные о номере и его удобствах.
        """
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)

        # print(rooms_ids_to_get.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        # logger.debug("SQL: %s", query.compile(dialect=PostgreSQLDialect(), compile_kwargs={"literal_binds": True}))

        query = (
            select(self.model)  # type: ignore
            .options(selectinload(self.model.facilities))
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))  # type: ignore
        )
        result = await self.session.execute(query)

        return [
            RoomDataWithRelsMapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_one_with_rels(self, **filter_by):
        """
        Возвращает один номер с загруженными удобствами.

        Параметры:
        - **filter_by: Условия фильтрации (например, id=1, hotel_id=5).

        Логика:
        - Выполняет `SELECT ... JOIN facilities`.
        - Использует `selectinload` для избежания проблемы N+1.
        - Если номер не найден — выбрасывает `RoomNotFoundException`.

        Исключения:
        - RoomNotFoundException: если номер не существует.

        Возвращает:
        - Pydantic-схему `RoomWithRels`.
        """
        query = (
            select(self.model).options(selectinload(self.model.facilities)).filter_by(**filter_by)  # type: ignore
        )
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise RoomNotFoundException
        return RoomDataWithRelsMapper.map_to_domain_entity(model)

    async def get_by_title_in_hotel(self, hotel_id: int, title: str) -> RoomsOrm:
        """Возвращает номер по названию и отелю, если найден."""
        query = select(self.model).where(self.model.hotel_id == hotel_id, self.model.title == title)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
