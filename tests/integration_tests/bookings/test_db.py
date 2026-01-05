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
    new_booking = await db.bookings.add(booking_data)

    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert booking
    assert booking.id == new_booking.id
    assert booking.room_id == new_booking.room_id
    assert booking.user_id == new_booking.user_id

    update_date = date(year=2023, month=12, day=25)
    update_booking_data = BookingAdd(
        user_id=user_id,
        room_id=room_id,
        date_from=date(year=2023, month=12, day=10),
        date_to=update_date,
        price=100,
    )
    await db.bookings.edit(update_booking_data, id=new_booking.id)
    updated_booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert updated_booking
    assert updated_booking.id == new_booking.id
    assert updated_booking.date_to == update_date

    await db.bookings.delete(id=new_booking.id)
    booking = await db.bookings.get_one_or_none(id=new_booking.id)
    assert not booking
