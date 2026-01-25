from datetime import date

from fastapi import APIRouter, Body, Query
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.exceptions import HotelNotFoundHTTPException, \
    RoomNotFoundHTTPException, RoomNotFoundException, HotelNotFoundException
from src.schemas.rooms import RoomAddRequest, RoomPatchRequest
from src.services.rooms import RoomService

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/{hotel_id}/rooms")
@cache(expire=10)
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2025-12-29"),
    date_to: date = Query(example="2025-12-31"),
):
    return await RoomService(db).get_filtered_by_time(hotel_id, date_from, date_to)


@router.get("/{hotel_id}/rooms/{room_id}")
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


@router.post("/{hotel_id}/rooms")
async def create_room(
    db: DBDep,
    hotel_id: int,
    room_data: RoomAddRequest = Body(),
):
    try:
        room = await RoomService(db).create_room(hotel_id, room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"Status": "Ok", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def edit_room(
    db: DBDep,
    hotel_id: int,
    room_id: int,
    room_data: RoomAddRequest,
):
    await RoomService(db).edit_room(hotel_id, room_id, room_data)

    return {"Status": "Ok", "message": "Номер успешно изменен"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def partially_edit_room(
        db: DBDep,
        hotel_id: int,
        room_id: int,
        room_data: RoomPatchRequest
):
    await RoomService(db).partially_edit_room(hotel_id, room_id, room_data)
    return {"Status": "Ok", "Message": "Номер успешно изменён"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(
    hotel_id: int,
    room_id: int,
    db: DBDep,
):
    await RoomService(db).delete_room(hotel_id, room_id)
    return {"Status": "Ok", "Message": "Номер Удалён"}
