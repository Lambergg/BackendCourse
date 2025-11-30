from src.repositories.base import BaseRepository
from src.models.rooms import RoomsOrm
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
