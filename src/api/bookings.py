from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get(
    "",
    summary="Получить все бронирования",
    description="<h1>Получаем все бронирования</h1>",
)
@cache(expire=10)
async def get_bookings(
    db: DBDep,
):
    """
    Возвращает список всех бронирований.

    Параметры:
    - db (DBDep): Зависимость для работы с базой данных.

    Логика:
    - Вызывает сервис `BookingService(db).get_bookings()`.
    - Сервис получает все записи из таблицы `bookings`.

    Кэширование:
    - Результат кэшируется на 10 секунд через `fastapi-cache`.

    Возвращает:
    - Список всех бронирований.
    """
    return await BookingService(db).get_bookings()


@router.get(
    "/me",
    summary="Получить все бронирования пользователя",
    description="<h1>Получаем все бронирования пользователя</h1>",
)
@cache(expire=10)
async def get_my_bookings(user_id: UserIdDep, db: DBDep):
    """
    Возвращает бронирования текущего пользователя.

    Параметры:
    - user_id (UserIdDep): ID аутентифицированного пользователя (извлекается из JWT).
    - db (DBDep): Зависимость для работы с БД.

    Логика:
    - Передаёт `user_id` в сервис.
    - Сервис фильтрует бронирования по `user_id`.

    Кэширование:
    - Результат кэшируется на 10 секунд.
    - Ключ кэша зависит от `user_id`.

    Возвращает:
    - Список бронирований текущего пользователя.
    """
    return await BookingService(db).get_my_bookings(user_id)


@router.post(
    "",
    summary="Добавить бронирование",
    description="<h1>Для добавления нужно передать id номера и даты заезда и выезда</h1>",
)
async def add_booking(
    user_id: UserIdDep,
    db: DBDep,
    booking_data: BookingAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Новое бронирование",
                "value": {
                    "room_id": 1,
                    "date_from": "2026-01-25",
                    "date_to": "2026-01-31",
                },
            },
        }
    ),
):
    """
    Добавляет новое бронирование.

    Параметры:
    - user_id (UserIdDep): ID пользователя из JWT-токена.
    - db (DBDep): Зависимость для работы с БД.
    - booking_data (BookingAddRequest): Данные для бронирования:
        * room_id — ID номера
        * date_from — дата заезда
        * date_to — дата выезда

    Логика:
    1. Передаёт данные в `BookingService.add_booking()`.
    2. Сервис:
        - Проверяет, что номер доступен в указанные даты.
        - Проверяет, что дата заезда < даты выезда.
        - Создаёт запись в БД.
    3. При успехе — возвращает созданное бронирование.

    Возвращает:
    - JSON: {"Status": "Ok", "data": {...}}
    """
    booking = await BookingService(db).add_booking(user_id, booking_data)
    return {"Status": "Ok", "data": booking}
