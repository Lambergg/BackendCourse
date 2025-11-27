from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from src.database import Base


class RoomsOrm(Base):
    """
    ORM model representing the 'rooms' table in the database.

    This class defines the structure of the 'rooms' table using SQLAlchemy's
    declarative mapping system. Each instance of this class corresponds to a
    row in the 'rooms' table, representing a room within a hotel.

    Attributes:
        __tablename__ (str): The name of the database table associated
                             with this model.

        id (Mapped[int]): The primary key of the room. A unique identifier
                          for each room in the system.

        hotel_id (Mapped[int]): Foreign key referencing the 'id' column of
                                the 'hotels' table. Establishes a relationship
                                between a room and its parent hotel.

        title (Mapped[str]): The name or title of the room (e.g., "Deluxe Suite").
                             Stored as a string.

        description (Mapped[str | None]): Optional description of the room.
                                          Can be null in the database.

        price (Mapped[int]): The price of booking the room, represented in the
                             smallest currency unit (e.g., cents or kopeks)
                             to avoid floating-point precision issues.

        quantity (Mapped[int]): The number of rooms of this type available
                                in the hotel.
    """
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    title: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]
