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
    return await BookingService(db).get_bookings()


@router.get(
    "/me",
    summary="Получить все бронирования пользователя",
    description="<h1>Получаем все бронирования пользователя</h1>",
)
@cache(expire=10)
async def get_my_bookings(user_id: UserIdDep, db: DBDep):
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
    booking = await BookingService(db).add_booking(user_id, booking_data)
    return {"Status": "Ok", "data": booking}
