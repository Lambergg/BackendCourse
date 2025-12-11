from datetime import date

from sqlalchemy import select, func

from src.models.rooms import RoomsOrm
from src.repositories.base import BaseRepository
from src.models.hotels import HotelsOrm
from src.repositories.utils import rooms_ids_for_booking
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    """
    Repository class for handling database operations related to the Hotel entity.

    This class extends the BaseRepository to provide specific functionality
    for the HotelsOrm model and Hotel schema. It encapsulates all data access
    logic for hotel records, including advanced filtering and pagination.

    The repository uses the BaseRepository's generic methods while specifying
    the concrete model and schema to work with, enabling type-safe operations
    and automatic serialization/deserialization between ORM objects and
    Pydantic models. It also provides a custom implementation of get_all
    with filtering capabilities by location and title.

    Attributes:
        model (type[HotelsOrm]): The ORM model class that this repository manages.
            Specifies that this repository works with the HotelsOrm model.
        schema (type[Hotel]): The Pydantic schema class used for data validation
            and serialization. Specifies that results should be returned as
            Hotel schema instances.
    """
    model = HotelsOrm
    schema = Hotel

    async def get_filtered_by_time(
            self,
            date_from: date,
            date_to: date,
            location,
            title,
            limit,
            offset,
    ) -> list[Hotel]:

        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
        hotels_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        query = select(HotelsOrm).filter(HotelsOrm.id.in_(hotels_ids_to_get))
        if location:
            query = query.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))
        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)

        return [Hotel.model_validate(hotel, from_attributes=True) for hotel in result.scalars().all()]
