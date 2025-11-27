from sqlalchemy import select, func

from src.repositories.base import BaseRepository
from src.models.hotels import HotelsOrm
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

    async def get_all(
            self,
            location,
            title,
            limit,
            offset,
    ) -> list[Hotel]:
        """
                Retrieve a paginated list of hotels with optional filtering by location and title.

                Performs a case-insensitive search for hotels whose location or title contains
                the specified substrings. Returns results within the specified pagination bounds.

                The search is performed using SQL's LIKE operator via the contains() method,
                with both search terms converted to lowercase for case-insensitive matching.

                Args:
                    location (str | None): Filter criterion for hotel location.
                        If provided, only hotels whose location contains this substring
                        (case-insensitive) will be returned. Leading/trailing whitespace is stripped.
                    title (str | None): Filter criterion for hotel title.
                        If provided, only hotels whose title contains this substring
                        (case-insensitive) will be returned. Leading/trailing whitespace is stripped.
                    limit (int): Maximum number of results to return. Used for pagination.
                    offset (int): Number of results to skip before returning records. Used for pagination.

                Returns:
                    list[Hotel]: A list of Hotel schema objects matching the criteria.
                        Returns an empty list if no hotels match the criteria.
                        Each hotel is validated and converted from ORM model to Pydantic schema.

                Example:
                    repo = HotelsRepository(session)
                    hotels = await repo.get_all(
                    location="sochi",
                    title="luxury",
                    limit=10,
                    offset=0
                    )
                    len(hotels)
                    3

                Note:
                    The method prints the compiled SQL query with literal values for debugging purposes.
                    This should be removed or disabled in production environments.
                """
        query = select(HotelsOrm)
        if location:
            query = query.filter(func.lower(HotelsOrm.location).contains(location.strip().lower()))
        if title:
            query = query.filter(func.lower(HotelsOrm.title).contains(title.strip().lower()))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)

        return [Hotel.model_validate(hotel, from_attributes=True) for hotel in result.scalars().all()]
