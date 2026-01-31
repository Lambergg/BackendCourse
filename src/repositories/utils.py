from datetime import date

from sqlalchemy import func, select, Select, Subquery

from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm


def rooms_ids_for_booking(
    date_from: date,
    date_to: date,
    hotel_id: int | None = None,
) -> Select:
    rooms_count = (
        select(BookingsOrm.room_id, func.count("*").label("rooms_reserved"))
        .select_from(BookingsOrm)
        .filter(
            BookingsOrm.date_from <= date_to,
            BookingsOrm.date_to >= date_from,
        )
        .group_by(BookingsOrm.room_id)
        .cte(name="rooms_count")
    )

    rooms_left_result = (
        select(
            RoomsOrm.id.label("rooms_id"),
            (RoomsOrm.quantity - func.coalesce(rooms_count.c.rooms_reserved, 0)).label(
                "rooms_left"
            ),
        )
        .select_from(RoomsOrm)
        .outerjoin(rooms_count, RoomsOrm.id == rooms_count.c.room_id)
        .cte(name="rooms_left_result")
    )

    rooms_ids_for_hotel = select(RoomsOrm.id).select_from(RoomsOrm)
    if hotel_id is not None:
        rooms_ids_for_hotel = rooms_ids_for_hotel.filter_by(hotel_id=hotel_id)

    rooms_ids_for_hotel_subq: Subquery = rooms_ids_for_hotel.subquery(name="rooms_ids_from_hotel")

    rooms_ids_to_get = (
        select(rooms_left_result.c.rooms_id)
        .select_from(rooms_left_result)
        .filter(
            rooms_left_result.c.rooms_left > 0,
            rooms_left_result.c.rooms_id.in_(rooms_ids_for_hotel_subq.select()),  # type: ignore
        )
    )

    return rooms_ids_to_get
