from datetime import date
from typing import Sequence

from sqlalchemy import select

from src.exceptions import AllRoomsAreBookedException
from src.repositories.base import BaseRepository
from src.models.bookings import BookingsOrm
from src.repositories.mappers.mappers import BookingDataMapper
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.bookings import BookingAdd


class BookingsRepository(BaseRepository):
    """
    Репозиторий для работы с бронированиями.

    Наследуется от BaseRepository и предоставляет специфичные методы:
    - Получение бронирований с заездом сегодня.
    - Добавление нового бронирования с проверкой доступности номера.

    Атрибуты:
    - model: ORM-модель `BookingsOrm`.
    - mapper: Маппер `BookingDataMapper` для преобразования в Pydantic-схему.
    """

    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self):
        """
        Возвращает все бронирования, у которых дата заезда — сегодня.

        Используется, например, для уведомлений или статистики.

        Логика:
        - Выполняет запрос: SELECT * FROM bookings WHERE date_from = CURRENT_DATE.
        - Преобразует результаты через маппер.

        Возвращает:
        - Список Pydantic-схем `Booking`.
        """
        query = select(BookingsOrm).filter(BookingsOrm.date_from == date.today())
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def add_booking(self, data: BookingAdd, hotel_id: int):
        """
        Добавляет новое бронирование, если номер доступен в указанный период.

        Параметры:
        - data (BookingAdd): Данные для бронирования (room_id, date_from, date_to, цена).
        - hotel_id (int): ID отеля (нужен для проверки доступности).

        Логика:
        1. Формирует SQL-запрос (CTE) для получения ID доступных номеров в заданный период.
        2. Выполняет запрос через `rooms_ids_for_booking()`.
        3. Проверяет, входит ли `data.room_id` в список свободных.
        4. Если да — создаёт бронирование.
        5. Если нет — выбрасывает исключение `AllRoomsAreBookedException`.

        Исключения:
        - AllRoomsAreBookedException: если номер уже забронирован.

        Возвращает:
        - Созданное бронирование как Pydantic-схему.
        """
        rooms_ids_to_get = rooms_ids_for_booking(
            date_from=data.date_from,
            date_to=data.date_to,
            hotel_id=hotel_id,
        )
        rooms_ids_to_book_res = await self.session.execute(rooms_ids_to_get)
        rooms_ids_to_book: Sequence[int] = rooms_ids_to_book_res.scalars().all()

        if data.room_id in rooms_ids_to_book:
            new_booking = await self.add(data)
            return new_booking

        raise AllRoomsAreBookedException
