from datetime import date
from fastapi import Query, APIRouter, Body, Path
from fastapi_cache.decorator import cache

from src.api.dependencies import PaginationDep, DBDep
from src.exceptions import ObjectNotFoundException, HotelNotFoundHTTPException
from src.schemas.hotels import HotelPatch, HotelAdd
from src.services.hotels import HotelService

router = APIRouter(prefix="/hotels", tags=["Отели"])


# GET-запрос для получения списка отелей
@router.get(
    "",
    summary="Получение всех отелей",
    description="<h1>Тут мы получаем выбранный отель или все отели: "
    "можно указать id, title, page и per_page, либо ничего для всех отлей</h1>",
)
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    title: str | None = Query(None, description="Название отеля"),
    location: str | None = Query(None, description="Адресс отеля"),
    date_from: date = Query(example="2025-12-29"),
    date_to: date = Query(example="2025-12-31"),
):
    """
    Возвращает список отелей с фильтрацией по названию, местоположению и доступности номеров.

    Параметры:
    - pagination (PaginationDep): Параметры пагинации (page, per_page).
    - db (DBDep): Зависимость для работы с базой данных.
    - title (str | None): Фильтр по названию отеля.
    - location (str | None): Фильтр по адресу.
    - date_from (date): Дата заезда — используется для проверки доступных номеров.
    - date_to (date): Дата выезда.

    Логика:
    - Вызывает `HotelService.get_filtered_by_time()` → CTE-запрос с подсчётом свободных номеров.
    - Результат кэшируется на 10 секунд.

    Возвращает:
    - Список отелей с количеством доступных номеров в указанный период.
    """
    return await HotelService(db).get_filtered_by_time(
        pagination,
        title,
        location,
        date_from,
        date_to,
    )


# GET-запрос для получения конкретного отеля
@router.get(
    "/{hotel_id}",
    summary="Получение конкретного отеля",
    description="<h1>Тут мы получаем выбранный отель, нужно указать id</h1>",
)
@cache(expire=10)
async def get_hotel(
    db: DBDep,
    hotel_id: int = Path(..., le=9223372036854775807),
):
    """
    Возвращает данные одного отеля по его ID.

    Параметры:
    - hotel_id (int): Уникальный идентификатор отеля.
    - db (DBDep): Зависимость для работы с БД.

    Логика:
    - Получает отель через `HotelService.get_hotel()`.
    - Если отель не найден — выбрасывается исключение.

    Возвращает:
    - Pydantic-модель отеля.
    """
    try:
        return await HotelService(db).get_hotel(hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException


# POST-запрос для добавления нового отеля
@router.post(
    "",
    summary="Добавление нового отеля",
    description="<h1>Тут мы добавляем отель: нужно отправить name и title</h1>",
)
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {
                    "title": "Отель Сочи 5 звёзд у моря",
                    "location": "ул.Морская д.10",
                },
            },
            "2": {
                "summary": "Дубай",
                "value": {
                    "title": "Отель Дубай у фонтана",
                    "location": "ул.Шейха д.1",
                },
            },
        }
    ),
):
    """
    Добавляет новый отель в систему.

    Параметры:
    - db (DBDep): Зависимость для работы с БД.
    - hotel_data (HotelAdd): Данные нового отеля — название и адрес.

    Логика:
    - Передаёт данные в `HotelService.add_hotel()`.
    - Создаёт запись в таблице `hotels`.

    Возвращает:
    - JSON: {"Status": "Ok", "data": {...}} — созданный отель.
    """
    hotel = await HotelService(db).add_hotel(hotel_data)
    return {"Status": "Ok", "data": hotel}


# PUT-запрос для полного обновления отеля
@router.put(
    "/{hotel_id}",
    summary="Полное обновление выбранного отеля",
    description="<h1>Тут мы обновляем выбранный отель: нужно отправить name и title</h1>",
)
async def edit_hotel(
    db: DBDep,
    hotel_id: int = Path(..., le=9223372036854775807),
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Новые данные",
                "value": {
                    "title": "Мега отель у моря",
                    "location": "ул.Мега Гига.10",
                },
            },
        }
    ),
):
    """
    Полностью заменяет данные существующего отеля.

    Параметры:
    - hotel_id (int): ID отеля.
    - db (DBDep): Зависимость для работы с БД.
    - hotel_data (HotelAdd): Новые данные отеля (обязательные поля).

    Логика:
    - Обновляет все поля отеля.
    - Если отель не найден — выбрасывается исключение.

    Возвращает:
    - JSON: {"Status": "Ok", "Message": "Отель изменён"}
    """
    await HotelService(db).edit_hotel(hotel_id, hotel_data, exclude_unset=False)
    return {"Status": "Ok", "Message": "Отель изменён"}


# PATCH-запрос для частичного обновления отеля
@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>",
)
async def partially_edit_hotel(
    db: DBDep,
    hotel_id: int = Path(..., le=9223372036854775807),
    hotel_data: HotelPatch = Body(
        openapi_examples={
            "1": {
                "summary": "Новые данные",
                "value": {
                    "title": "Тут мы обновляем данные об отеле",
                    "location": "А это мы не обновляем. Или можем обновить и то и то",
                },
            },
        }
    ),
):
    """
    Частично обновляет данные отеля.

    Параметры:
    - hotel_id (int): ID отеля.
    - db (DBDep): Зависимость для работы с БД.
    - hotel_data (HotelPatch): Поля для обновления (опциональные).

    Логика:
    - Обновляет только переданные поля.
    - Использует `exclude_unset=True` → пропускает непереданные поля.

    Возвращает:
    - JSON: {"Status": "Ok", "Message": "Отель изменён"}
    """
    await HotelService(db).edit_hotel_partially(hotel_id, hotel_data, exclude_unset=True)
    return {"Status": "Ok", "Message": "Отель изменён"}


# DELETE-запрос для удаления отеля
@router.delete(
    "/{hotel_id}",
    summary="Удаление выбранного отеля",
    description="<h1>Тут мы удалем выбранный отель: нужно отправить id отеля</h1>",
)
async def delete_hotel(
    db: DBDep,
    hotel_id: int = Path(..., le=9223372036854775807),
):
    """
    Удаляет отель по ID.

    Параметры:
    - hotel_id (int): ID отеля.
    - db (DBDep): Зависимость для работы с БД.

    Логика:
    - Вызывает `HotelService.delete_hotel()`.
    - Удаляет отель из БД.

    Возвращает:
    - JSON: {"Status": "Ok", "Message": "Отель Удалён"}
    """
    await HotelService(db).delete_hotel(hotel_id)
    return {"Status": "Ok", "Message": "Отель Удалён"}
