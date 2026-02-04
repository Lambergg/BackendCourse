from datetime import date

from src.exceptions import check_date_to_after_date_from, ObjectNotFoundException, HotelNotFoundException
from src.schemas.hotels import HotelAdd, HotelPatch, Hotel
from src.services.base import BaseService


class HotelService(BaseService):
    """
    Сервис для управления отелями.

    Предоставляет методы:
    - Получение отелей с фильтрацией по времени и локации.
    - Получение, создание, обновление и удаление отелей.
    - Проверка существования отеля.

    Наследуется от `BaseService`, имеет доступ к `self.db` (DBManager).
    """
    async def get_filtered_by_time(
            self,
            pagination,
            title: str | None,
            location: str | None,
            date_from: date,
            date_to: date,
    ):
        """
        Возвращает отели с доступными номерами в указанный период.

        Параметры:
        - pagination: Объект с page и per_page.
        - title: Фильтр по названию отеля.
        - location: Фильтр по местоположению.
        - date_from: Дата заезда.
        - date_to: Дата выезда.

        Логика:
        1. Проверяет, что date_from < date_to.
        2. Рассчитывает limit и offset для пагинации.
        3. Передаёт параметры в репозиторий `hotels.get_filtered_by_time()`.

        Возвращает:
        - Список Pydantic-схем `Hotel`, соответствующих условиям.
        """
        check_date_to_after_date_from(date_from, date_to)
        per_page = pagination.per_page or 5
        return await self.db.hotels.get_filtered_by_time(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
        )

    async def get_hotel(self, hotel_id: int):
        """
        Возвращает данные отеля по ID.

        Параметры:
        - hotel_id (int): ID отеля.

        Логика:
        - Вызывает `self.db.hotels.get_one(id=hotel_id)`.

        Возвращает:
        - Pydantic-схему `Hotel`.
        """
        return await self.db.hotels.get_one(id=hotel_id)

    async def add_hotel(self, data: HotelAdd):
        """
        Добавляет новый отель в систему.

        Параметры:
        - data (HotelAdd): Данные нового отеля — название и адрес.

        Логика:
        1. Сохраняет отель через `self.db.hotels.add(data)`.
        2. Фиксирует транзакцию.

        Возвращает:
        - Созданный отель как Pydantic-схему.
        """
        hotel = await self.db.hotels.add(data)
        await self.db.commit()
        return hotel

    async def edit_hotel(self, hotel_id: int, data: HotelAdd):
        """
        Полностью обновляет данные отеля.

        Параметры:
        - hotel_id (int): ID отеля.
        - data (HotelAdd): Новые данные отеля.

        Логика:
        1. Обновляет все поля отеля.
        2. Фиксирует изменения.

        Возвращает:
        - None.
        """
        await self.db.hotels.edit(data, id=hotel_id)
        await self.db.commit()

    async def edit_hotel_partially(self, hotel_id: int, data: HotelPatch, exclude_unset: bool = False):
        """
        Частично обновляет данные отеля.

        Параметры:
        - hotel_id (int): ID отеля.
        - data (HotelPatch): Поля для обновления.
        - exclude_unset (bool): Если True — обновляются только переданные поля.

        Логика:
        - Использует `exclude_unset=True` → пропускает непереданные поля.
        - Фиксирует изменения.

        Возвращает:
        - None.
        """
        await self.db.hotels.edit(data, exclude_unset=exclude_unset, id=hotel_id)
        await self.db.commit()

    async def delete_hotel(self, hotel_id: int):
        """
        Удаляет отель по ID.

        Параметры:
        - hotel_id (int): ID отеля.

        Логика:
        - Удаляет запись из БД.
        - Фиксирует транзакцию.

        Возвращает:
        - None.
        """
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()

    async def get_hotel_with_check(self, hotel_id: int) -> Hotel:
        """
        Возвращает отель с проверкой на существование.

        Параметры:
        - hotel_id (int): ID отеля.

        Логика:
        - Пытается получить отель.
        - Если не найден — выбрасывает `HotelNotFoundException`.

        Исключения:
        - HotelNotFoundException: если отель не существует.

        Возвращает:
        - Pydantic-схему `Hotel`.
        """
        try:
            return await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException
