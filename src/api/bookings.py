from fastapi import APIRouter, HTTPException
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep, UserIdDep
from src.exceptions import ObjectNotFoundException, AllRoomsAreBookedException
from src.schemas.bookings import BookingAddRequest, BookingAdd
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.get("")
@cache(expire=10)
async def get_bookings(
    db: DBDep,
):
    return await BookingService(db).get_bookings()


@router.get("/me")
@cache(expire=10)
async def get_my_bookings(user_id: UserIdDep, db: DBDep):
    return await BookingService(db).get_my_bookings(user_id)


@router.post("")
async def add_booking(
    user_id: UserIdDep,
    db: DBDep,
    booking_data: BookingAddRequest,
):
    booking = await BookingService(db).add_booking(user_id, booking_data)
    return {"Status": "Ok", "data": booking}
