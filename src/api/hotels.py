from datetime import date
from fastapi import Query, APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import PaginationDep, DBDep
from src.exceptions import check_date_to_after_date_from, ObjectNotFoundException, HotelNotFoundHTTPException
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
    hotel_id: int,
    db: DBDep,
):
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
    hotel = await HotelService(db).add_hotel(hotel_data)
    return {"Status": "Ok", "data": hotel}


# PUT-запрос для полного обновления отеля
@router.put(
    "/{hotel_id}",
    summary="Полное обновление выбранного отеля",
    description="<h1>Тут мы обновляем выбранный отель: нужно отправить name и title</h1>",
)
async def edit_hotel(
    hotel_id: int,
    hotel_data: HotelAdd,
    db: DBDep,
):
    await HotelService(db).edit_hotel(hotel_id, hotel_data)
    return {"Status": "Ok", "Message": "Отель изменён"}


# PATCH-запрос для частичного обновления отеля
@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>",
)
async def partially_edit_hotel(
    hotel_id: int,
    hotel_data: HotelPatch,
    db: DBDep,
):
    await HotelService(db).edit_hotel_partially(hotel_id, hotel_data, exclude_unset=True)
    return {"Status": "Ok", "Message": "Отель изменён"}


# DELETE-запрос для удаления отеля
@router.delete(
    "/{hotel_id}",
    summary="Удаление выбранного отеля",
    description="<h1>Тут мы удалем выбранный отель: нужно отправить id отеля</h1>",
)
async def delete_hotel(
    hotel_id: int,
    db: DBDep,
):
    await HotelService(db).delete_hotel(hotel_id)
    return {"Status": "Ok", "Message": "Отель Удалён"}
