from datetime import date

from sqlalchemy import select, func

from src.models.bookings import BookingsOrm
from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    """
    Repository class for handling database operations related to the Room entity.

    This class extends the BaseRepository to provide specific functionality
    for the RoomsOrm model. It inherits all generic CRUD operations from
    the base class while specifying the concrete model to work with.

    The repository encapsulates all data access logic for room records,
    enabling type-safe operations and automatic serialization/deserialization
    between ORM objects and Pydantic models through the base class implementation.

    Attributes:
        model (type[RoomsOrm]): The ORM model class that this repository manages.
            Specifies that this repository works with the RoomsOrm model.
    """
    model = RoomsOrm
    schema = Room

    async def get_filtered_by_time(
            self,
            hotel_id: int,
            date_from: date,
            date_to: date
    ):
        """
        -- CTE общее табличное выражение
            with rooms_count as (
                select room_id, count(*) as rooms_reserved from bookings
                where date_from <= '2025-12-31' and date_to >= '2025-12-29'
                group by room_id
            ),
            rooms_left_result as (
                select rooms.id as room_id, quantity - coalesce(rooms_reserved, 0) as rooms_left
                from rooms
                left join rooms_count on rooms.id = rooms_count.room_id
            )
            select * from rooms_left_result
            where rooms_left > 0
            ;
        """
        rooms_ids_to_get = rooms_ids_for_booking(hotel_id, date_from, date_to)

        #print(rooms_ids_to_get.compile(bind=engine, compile_kwargs={"literal_binds": True}))

        return await self.get_filtered(RoomsOrm.id.in_(rooms_ids_to_get))
