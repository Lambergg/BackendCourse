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
    await RoomService(db).delete_room(hotel_id, room_id)
    return {"Status": "Ok", "Message": "Номер Удалён"}
