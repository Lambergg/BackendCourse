from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
from src.repositories.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper
from src.repositories.utils import rooms_ids_for_booking


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    mapper = RoomDataMapper

    async def get_filtered_by_time(self, hotel_id: int, date_from: date, date_to: date):
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
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)

        # print(rooms_ids_to_get.compile(bind=engine, compile_kwargs={"literal_binds": True}))

        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )
        result = await self.session.execute(query)

        return [
            RoomDataWithRelsMapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_one_or_none_with_rels(self, **filter_by):
        query = (
            select(self.model).options(selectinload(self.model.facilities)).filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return RoomDataWithRelsMapper.map_to_domain_entity(model)
