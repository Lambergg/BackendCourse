from datetime import date

from src.schemas.bookings import BookingAdd


async def test_add_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2023, month=12, day=10),
        date_to=date(year=2023, month=12, day=20),
        price=100,
    )
    await db.bookings.add(booking_data)
    await db.commit()


async def test_get_booking_crud(db):
    await db.bookings.get_all()


async def test_edit_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2023, month=12, day=10),
        date_to=date(year=2023, month=12, day=20),
        price=1000,
    )
    await db.bookings.edit(booking_data)
    await db.commit()


async def test_delete_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    await db.bookings.delete(id=user_id)
    await db.commit()
