from fastapi import Query, APIRouter, Body

from dependencies import PaginationDep
from schemas.hotels import Hotel, HotelPATCH


router = APIRouter(prefix="/hotels", tags=["Отели"])


# Список отелей, используемый для хранения данных
hotels = [
    {"id": 1, "title": "Сочи", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "dubai"},
    {"id": 3, "title": "Мальдивы", "name": "maldivi"},
    {"id": 4, "title": "Геленджик", "name": "gelendzhik"},
    {"id": 5, "title": "Москва", "name": "moscow"},
    {"id": 6, "title": "Казань", "name": "kazan"},
    {"id": 7, "title": "Санкт-Петербург", "name": "spb"},
]


# GET-запрос для получения списка отелей
@router.get(
    "",
    summary="Получение отеля",
    description="<h1>Тут мы получаем выбранный отель или все отели: "
                "можно указать id, title, name, page и per_page, либо ничего для всех отлей</h1>",
)
def get_hotels(
        pagination: PaginationDep,
        id: int | None = Query(None, description="ID отеля"),
        title: str | None = Query(None, description="Название отеля"),
        name: str | None = Query(None, description="Наименование отеля"),
):
    """
        Получаем список отелей, фильтруя по параметрам:
        - `id`: ID отеля
        - `title`: Название отеля
        - `name`: Наименование отеля

        Если никакие параметры не указаны, возвращаем полный список отелей.
        """
    # Фильтруем отели согласно переданным параметрам
    hotels_ = []
    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        if name and hotel["name"] != name:
            continue
        hotels_.append(hotel)

    if pagination.page and pagination.per_page:
        return hotels_[pagination.per_page * (pagination.page-1):][:pagination.per_page]
    return hotels_


# POST-запрос для добавления нового отеля
@router.post(
    "",
    summary="Добавление нового отеля",
    description="<h1>Тут мы добавляем отель: нужно отправить name и title</h1>",
)
def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {"summary": "Сочи", "value": {
        "title": "Отель Сочи 5 звёзд у моря",
        "name": "sochi_u_morya",
    }}, "2": {"summary": "Дубай", "value": {
        "title": "Отель Дубай у фонтана",
        "name": "dubai_fountain",
    }},
})
):
    """
        Добавляет новый отель в базу данных:
        - `title`: название отеля
        - `name`: наименование отеля

        Возвращает статус операции и сообщение об успешном создании.
        """
    global hotels
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "title": hotel_data.title,
        "name": hotel_data.name
    })
    return {"Status": "Ok", "Message": "Отель добавлен"}


# PUT-запрос для полного обновления отеля
@router.put(
    "/{hotel_id}",
    summary="Полное обновление выбранного отеля",
    description="<h1>Тут мы обновляем выбранный отель: нужно отправить name и title</h1>",
)
def edit_hotel(hotel_id: int, hotel_data: Hotel):
    """
        Полностью обновляет информацию об отеле:
        - `hotel_id`: id отеля, который нужно обновить
        - `title`: новое название отеля
        - `name`: новое наименование отеля

        Возвращает статус операции и сообщение об успешном изменении.
        """
    global hotels
    hotel = [hotel for hotel in hotels if hotel["id"] == hotel_id][0]
    hotel["title"] = hotel_data.title
    hotel["name"] = hotel_data.name
    return {"Status": "Ok", "Message": "Отель изменён"}


# PATCH-запрос для частичного обновления отеля
@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>",
)
def partially_edit_hotel(
        hotel_id: int,
        hotel_data: HotelPATCH,
):
    """
        Частично обновляет информацию об отеле:
        - `hotel_id`: id отеля, который нужно обновить
        - `title` (необязательно): новое название отеля
        - `name` (необязательно): новое наименование отеля

        Возвращает статус операции и сообщение об успешном изменении.
        """
    global hotels
    hotel = [hotel for hotel in hotels if hotel["id"] == hotel_id][0]
    if hotel_data.title:
        hotel["title"] = hotel_data.title
    if hotel_data.name:
        hotel["name"] = hotel_data.name
    return {"Status": "Ok", "Message": "Отель изменён"}


# DELETE-запрос для удаления отеля
@router.delete(
    "/{hotel_id}",
    summary="Удаление выбранного отеля",
    description="<h1>Тут мы удалем выбранный отель: нужно отправить id отеля</h1>",
)
def delete_hotel(hotel_id: int):
    """
        Удаляет отель по переданному id:
        - `hotel_id`: id отеля, который нужно удалить

        Возвращает статус операции и сообщение об успешном удалении.
    """
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"Status": "Ok", "Message": "Отель Удалён"}