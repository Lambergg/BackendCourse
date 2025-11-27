from fastapi import Query, APIRouter, Body
from src.api.dependencies import PaginationDep
from src.database import async_session_maker
from src.repositories.hotels import HotelsRepository
from src.schemas.hotels import Hotel, HotelPATCH, HotelAdd

router = APIRouter(prefix="/hotels", tags=["Отели"])


# GET-запрос для получения списка отелей
@router.get(
    "",
    summary="Получение всех отелей",
    description="<h1>Тут мы получаем выбранный отель или все отели: "
                "можно указать id, title, page и per_page, либо ничего для всех отлей</h1>",
)
async def get_hotels(
        pagination: PaginationDep,
        title: str | None = Query(None, description="Название отеля"),
        location: str | None = Query(None, description="Адресс отеля"),
):
    """
    Получает список отелей с возможностью фильтрации и пагинации.

    Возвращает коллекцию отелей, соответствующих заданным параметрам.
    Поддерживается фильтрация по названию и местоположению,
    а также постраничный вывод результатов.

    Args:
        pagination (PaginationDep): Параметры пагинации, включающие номер страницы и количество элементов на странице.
                                   Внедряется через зависимость.
        title (str | None): Опциональный фильтр по названию отеля. Если указан, возвращаются только отели,
                            название которых содержит заданную строку.
        location (str | None): Опциональный фильтр по местоположению отеля. Если указан, возвращаются только отели,
                               расположенные по заданному адресу.

    Returns:
        Список отелей, соответствующих критериям фильтрации и пагинации.
        Если ни один отель не найден, возвращается пустой список.

    Example:
        GET /hotels?page=1&per_page=10&title=Сочи&location=Морская
    """
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(
            location=location,
            title=title,
            limit=per_page,
            offset=per_page * (pagination.page - 1)
        )


# GET-запрос для получения конкретного отеля
@router.get(
    "/{hotel_id}",
    summary="Получение конкретного отеля",
    description="<h1>Тут мы получаем выбранный отель, нужно указать id</h1>",
)
async def get_hotel(hotel_id: int):
    """
    Получает информацию об отеле по его уникальному идентификатору.

    Возвращает данные одного отеля или None, если отель с указанным ID не существует.

    Args:
        hotel_id (int): Уникальный идентификатор отеля, который необходимо получить.

    Returns:
        Информация об отеле в формате Pydantic-схемы.
        Если отель не найден, возвращается None.

    Example:
        GET /hotels/1
    """
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_one_or_none(id=hotel_id)


# POST-запрос для добавления нового отеля
@router.post(
    "",
    summary="Добавление нового отеля",
    description="<h1>Тут мы добавляем отель: нужно отправить name и title</h1>",
)
async def create_hotel(hotel_data: HotelAdd = Body(openapi_examples={
    "1": {"summary": "Сочи", "value": {
        "title": "Отель Сочи 5 звёзд у моря",
        "location": "ул.Морская д.10",
    }}, "2": {"summary": "Дубай", "value": {
        "title": "Отель Дубай у фонтана",
        "location": "ул.Шейха д.1",
    }},
})
):
    """
    Добавляет новый отель в систему.

    Создаёт запись нового отеля в базе данных на основе переданных данных.
    Требует полную информацию об отеле согласно схеме HotelAdd.

    Args:
        hotel_data (HotelAdd): Данные нового отеля, включая название и местоположение.
                              Принимается в теле запроса.

    Returns:
        dict: Словарь с результатом операции.
            - "Status": Статус выполнения операции ("Ok").
            - "data": Добавленный объект отеля.

    Example:
        POST /hotels
        {
            "title": "Отель Сочи 5 звёзд у моря",
            "location": "ул.Морская д.10"
        }
    """
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()

    return {"Status": "Ok", "data": hotel}


# PUT-запрос для полного обновления отеля
@router.put(
    "/{hotel_id}",
    summary="Полное обновление выбранного отеля",
    description="<h1>Тут мы обновляем выбранный отель: нужно отправить name и title</h1>",
)
async def edit_hotel(hotel_id: int, hotel_data: HotelAdd):
    """
    Полностью заменяет данные указанного отеля.

    Обновляет все поля отеля на основе переданных данных.
    Для успешного выполнения требуется предоставить полную информацию об отеле.

    Args:
        hotel_id (int): Идентификатор отеля, который необходимо обновить.
        hotel_data (HotelAdd): Новые данные отеля, включая название и местоположение.

    Returns:
        dict: Словарь с результатом операции.
            - "Status": Статус выполнения ("Ok").
            - "Message": Описание результата ("Отель изменён").

    Example:
        PUT /hotels/1
        {
            "title": "Обновлённый отель",
            "location": "Новый адрес"
        }
    """
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, id=hotel_id)
        await session.commit()
    return {"Status": "Ok", "Message": "Отель изменён"}


# PATCH-запрос для частичного обновления отеля
@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="<h1>Тут мы частично обновляем данные об отеле: можно отправить name, а можно title</h1>",
)
async def partially_edit_hotel(
        hotel_id: int,
        hotel_data: HotelPATCH,
):
    """
    Частично обновляет данные указанного отеля.

    Позволяет изменить только определённые поля отеля, не затрагивая остальные.
    Поля, которые не были переданы в запросе, сохраняют свои текущие значения.

    Args:
        hotel_id (int): Идентификатор отеля, который необходимо частично обновить.
        hotel_data (HotelPATCH): Данные для частичного обновления отеля.
                                 Могут включать любое подмножество полей.

    Returns:
        dict: Словарь с результатом операции.
            - "Status": Статус выполнения ("Ok").
            - "Message": Описание результата ("Отель изменён").

    Example:
        PATCH /hotels/1
        {
            "title": "Частично обновлённый отель"
        }
    """
    async with async_session_maker() as session:
        await HotelsRepository(session).edit(hotel_data, exclude_unset=True, id=hotel_id)
        await session.commit()
    return {"Status": "Ok", "Message": "Отель изменён"}


# DELETE-запрос для удаления отеля
@router.delete(
    "/{hotel_id}",
    summary="Удаление выбранного отеля",
    description="<h1>Тут мы удалем выбранный отель: нужно отправить id отеля</h1>",
)
async def delete_hotel(hotel_id: int):
    """
    Удаляет отель из системы по его идентификатору.

    Удаляет запись отеля из базы данных. Операция необратима.

    Args:
        hotel_id (int): Идентификатор отеля, который необходимо удалить.

    Returns:
        dict: Словарь с результатом операции.
            - "Status": Статус выполнения ("Ok").
            - "Message": Описание результата ("Отель Удалён").

    Example:
        DELETE /hotels/1
    """
    async with async_session_maker() as session:
        await HotelsRepository(session).delete(id=hotel_id)
        await session.commit()
    return {"Status": "Ok", "Message": "Отель Удалён"}
