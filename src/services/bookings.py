from src.exceptions import (
    ObjectNotFoundException,
    AllRoomsAreBookedException,
    AllRoomsAreBookedHTTPException,
    RoomNotFoundHTTPException,
)
from src.schemas.bookings import BookingAddRequest, BookingAdd
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room
from src.services.base import BaseService


class BookingService(BaseService):
    """
    Сервис для управления бронированиями.

    Предоставляет методы:
    - Получение всех бронирований.
    - Получение бронирований текущего пользователя.
    - Создание нового бронирования с проверкой доступности номера.

    Наследуется от `BaseService`, имеет доступ к `self.db` (DBManager).
    """

    async def get_bookings(self):
        """
        Возвращает все бронирования в системе.

        Используется, например, админом для просмотра всех броней.

        Логика:
        - Вызывает `self.db.bookings.get_all()`.

        Возвращает:
        - Список Pydantic-схем `Booking`.
        """
        return await self.db.bookings.get_all()

    async def get_my_bookings(self, user_id: int):
        """
        Возвращает все бронирования указанного пользователя.

        Параметры:
        - user_id (int): ID пользователя.

        Логика:
        - Фильтрует брони по `user_id`.

        Возвращает:
        - Список бронирований пользователя.
        """
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def add_booking(
        self,
        user_id: int,
        booking_data: BookingAddRequest,
    ):
        """
        Добавляет новое бронирование, если номер доступен.

        Параметры:
        - user_id (int): ID пользователя (из JWT-токена).
        - booking_data (BookingAddRequest): Данные для брони — room_id, date_from, date_to.

        Логика:
        1. Получает номер по `room_id`. Если не найден — ошибка.
        2. Получает отель по `room.hotel_id`.
        3. Берёт цену номера (`room.price`).
        4. Создаёт полную схему `BookingAdd` с `user_id` и `price`.
        5. Передаёт данные в `bookings_repository.add_booking()`, который проверяет доступность.
        6. При успехе — фиксирует транзакцию.

        Исключения:
        - RoomNotFoundHTTPException: если номер не существует.
        - AllRoomsAreBookedHTTPException: если номер уже забронирован в указанный период.

        Возвращает:
        - None (результат сохраняется в БД).
        """
        try:
            room: Room = await self.db.rooms.get_one(id=booking_data.room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundHTTPException
        hotel: Hotel = await self.db.hotels.get_one(id=room.hotel_id)
        room_price: int = room.price
        _booking_data = BookingAdd(user_id=user_id, price=room_price, **booking_data.model_dump())
        try:
            await self.db.bookings.add_booking(_booking_data, hotel_id=hotel.id)
        except AllRoomsAreBookedException:
            raise AllRoomsAreBookedHTTPException
        await self.db.commit()
