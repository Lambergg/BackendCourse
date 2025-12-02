from fastapi import APIRouter


from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd

router = APIRouter(prefix="/bookings", tags=["Бронирование"])


@router.post("")
async def add_booking(
        user_id: UserIdDep,
        db: DBDep,
        booking_data: BookingAddRequest,
):
    room = await db.rooms.get_one_or_none(id=booking_data.room_id)
    room_price: int = room.price
    _booking_data = BookingAdd(
        user_id=user_id,
        price=room_price,
        **booking_data.model_dump()
    )
    booking = await db.bookings.add(_booking_data)
    await db.commit()

    return {"Status": "Ok", "data": booking}


@router.get("/bookings")
async def get_bookings(
        room_id: int,
        db: DBDep,
):
    return await db.bookings.get_all(id=room_id)


@router.get("/bookings/me")
async def get_my_bookings(
        user_id: UserIdDep,
        db: DBDep
):
    bookigns = await db.bookings.get_all(id=user_id)
    return bookigns
