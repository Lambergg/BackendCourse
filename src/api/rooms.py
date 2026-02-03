from datetime import date

from fastapi import APIRouter, Body, Query
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.exceptions import HotelNotFoundHTTPException, \
    RoomNotFoundHTTPException, RoomNotFoundException, HotelNotFoundException
from src.schemas.rooms import RoomAddRequest, RoomPatchRequest
from src.services.rooms import RoomService

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get(
    "/{hotel_id}/rooms",
    summary="Получить все номера отеля",
    description="<h1>Для получения всех номеров отеля нужно указать id-отеля, а также даты заезда и выезда.</h1>",
)
@cache(expire=10)
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2025-12-29"),
    date_to: date = Query(example="2025-12-31"),
):
    """
    Возвращает список номеров указанного отеля с учётом доступности в заданный период.

    Параметры:
    - hotel_id (int): ID отеля.
    - db (DBDep): Зависимость для работы с базой данных.
    - date_from (date): Дата заезда — используется для проверки бронирований.
    - date_to (date): Дата выезда.

    Логика:
    - Вызывает `RoomService.get_filtered_by_time()` → CTE-запрос с подсчётом свободных номеров.
    - Результат кэшируется на 10 секунд.

    Возвращает:
    - Список номеров с информацией о цене, количестве, удобствах и доступных местах.
    """
    return await RoomService(db).get_filtered_by_time(hotel_id, date_from, date_to)


@router.get(
    "/{hotel_id}/rooms/{room_id}",
    summary="Получить номер",
    description="<h1>Для получения номера нужно указать id-отеля и id-номера.</h1>",
)
@cache(expire=10)
async def get_room(
    hotel_id: int,
    room_id: int,
    db: DBDep,
):
    """
    Возвращает данные одного номера по ID отеля и номера.

    Параметры:
    - hotel_id (int): ID отеля.
    - room_id (int): ID номера.
    - db (DBDep): Зависимость для работы с БД.

    Логика:
    - Получает номер через `RoomService.get_room()`.
    - Если не найден — выбрасывается исключение.

    Возвращает:
    - Pydantic-модель номера.
    """
    try:
        return await RoomService(db).get_room(hotel_id, room_id)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException


@router.post(
    "/{hotel_id}/rooms",
    summary="Создать номер",
    description="<h1>Для создания номера нужно указать id-отеля, цену, кол-во мест и удобства.</h1>",
)
async def create_room(
    db: DBDep,
    hotel_id: int,
    room_data: RoomAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Новый номер",
                "value": {
                    "title": "VIP 101",
                    "description": "Очень хороший номер",
                    "price": 1000,
                    "quantity": 6,
                    "facilities_ids": [1, 2, 3, 7]
                },
            },
        }
    ),
):
    """
    Добавляет новый номер в указанный отель.

    Параметры:
    - db (DBDep): Зависимость для работы с БД.
    - hotel_id (int): ID отеля.
    - room_data (RoomAddRequest): Данные нового номера — название, описание, цена, количество, удобства.

    Логика:
    - Передаёт данные в `RoomService.create_room()`.
    - Проверяет существование отеля.
    - Создаёт запись в таблице `rooms`.

    Возвращает:
    - JSON: {"Status": "Ok", "data": {...}} — созданный номер.
    """
    try:
        room = await RoomService(db).create_room(hotel_id, room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"Status": "Ok", "data": room}


@router.put(
    "/{hotel_id}/rooms/{room_id}",
    summary="Изменить номер",
    description="<h1>Для изменения номера нужно указать id-отеля и id-номера, цену, кол-во мест, удобства.</h1>",
)
async def edit_room(
    db: DBDep,
    hotel_id: int,
    room_id: int,
    room_data: RoomAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Новые данные",
                "value": {
                    "title": "VIP 102",
                    "description": "Очень хороший номер 2",
                    "price": 2000,
                    "quantity": 8,
                    "facilities_ids": [1, 2, 3, 4, 5, 6, 7]
                },
            },
        }
    ),
):
    """
    Полностью заменяет данные номера.

    Параметры:
    - db (DBDep): Зависимость для работы с БД.
    - hotel_id (int): ID отеля.
    - room_id (int): ID номера.
    - room_data (RoomAddRequest): Новые данные номера.

    Логика:
    - Обновляет все поля номера.
    - Если отель или номер не найдены — выбрасывается исключение.

    Возвращает:
    - JSON: {"Status": "Ok", "message": "Номер успешно изменен"}
    """
    await RoomService(db).edit_room(hotel_id, room_id, room_data)

    return {"Status": "Ok", "message": "Номер успешно изменен"}


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частично изменить номер",
    description="<h1>Для частичного изменения номера нужно указать id-отеля и id-номера, цену, кол-во мест, удобства.</h1>",
)
async def partially_edit_room(
        db: DBDep,
        hotel_id: int,
        room_id: int,
        room_data: RoomPatchRequest = Body(
        openapi_examples={
            "1": {
                "summary": "Новые данные",
                "value": {
                    "title": "VIP 103",
                    "description": "Очень хороший номер 3",
                    "price": 10000,
                    "quantity": 2,
                    "facilities_ids": [1, 2, 3]
                },
            },
        }
        )
):
    """
    Частично обновляет данные номера.

    Параметры:
    - db (DBDep): Зависимость для работы с БД.
    - hotel_id (int): ID отеля.
    - room_id (int): ID номера.
    - room_data (RoomPatchRequest): Поля для обновления (опциональные).

    Логика:
    - Обновляет только переданные поля.
    - Использует `exclude_unset=True` → пропускает непереданные поля.

    Возвращает:
    - JSON: {"Status": "Ok", "Message": "Номер успешно изменён"}
    """
    await RoomService(db).partially_edit_room(hotel_id, room_id, room_data)
    return {"Status": "Ok", "Message": "Номер успешно изменён"}


@router.delete(
    "/{hotel_id}/rooms/{room_id}",
    summary="Удалить номер",
    description="<h1>Для удаления номера нужно указать id-отеля и id-номера.</h1>",
)
async def delete_room(
    hotel_id: int,
    room_id: int,
    db: DBDep,
):
    """
    Удаляет номер по ID отеля и номера.

    Параметры:
    - hotel_id (int): ID отеля.
    - room_id (int): ID номера.
    - db (DBDep): Зависимость для работы с БД.

    Логика:
    - Вызывает `RoomService.delete_room()`.
    - Удаляет номер из БД.

    Возвращает:
    - JSON: {"Status": "Ok", "Message": "Номер Удалён"}
    """
    await RoomService(db).delete_room(hotel_id, room_id)
    return {"Status": "Ok", "Message": "Номер Удалён"}
