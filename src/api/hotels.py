from fastapi import Query, APIRouter, Body
from sqlalchemy import insert, select, func

from src.api.dependencies import PaginationDep
from src.database import async_session_maker, engine
from src.models.hotels import HotelsOrm
from src.schemas.hotels import Hotel, HotelPATCH


router = APIRouter(prefix="/hotels", tags=["Отели"])


# GET-запрос для получения списка отелей
@router.get(
    "",
    summary="Получение отеля",
    description="<h1>Тут мы получаем выбранный отель или все отели: "
                "можно указать id, title, page и per_page, либо ничего для всех отлей</h1>",
)
async def get_hotels(
        pagination: PaginationDep,
        title: str | None = Query(None, description="Название отеля"),
        location: str | None = Query(None, description="Адресс отеля"),
):
    per_page = pagination.per_page or 5
    async with (async_session_maker() as session):
        query = select(HotelsOrm)
        if location:
            query = query.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))
        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
        query = (
            query
            .limit(per_page)
            .offset(per_page * (pagination.page - 1))
        )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await session.execute(query)

        hotels = result.scalars().all()
        #print(type(hotels), hotels)
        return hotels

    #if pagination.page and pagination.per_page:
        #return hotels_[pagination.per_page * (pagination.page-1):][:pagination.per_page]



# POST-запрос для добавления нового отеля
@router.post(
    "",
    summary="Добавление нового отеля",
    description="<h1>Тут мы добавляем отель: нужно отправить name и title</h1>",
)
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {"summary": "Сочи", "value": {
        "title": "Отель Сочи 5 звёзд у моря",
        "location": "ул.Морская д.10",
    }}, "2": {"summary": "Дубай", "value": {
        "title": "Отель Дубай у фонтана",
        "location": "ул.Шейха д.1",
    }},
})
):

    async with async_session_maker() as session:
        add_hotel_stnt = insert(HotelsOrm).values(**hotel_data.model_dump())
        #print(add_hotel_stnt.compile(engine, compile_kwargs={"literal_binds": True}))
        await session.execute(add_hotel_stnt)
        await session.commit()

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