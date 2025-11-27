from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.database import Base


class HotelsOrm(Base):
    """
    ORM model representing the 'hotels' table in the database.

    This class defines the structure of the 'hotels' table using SQLAlchemy's
    declarative mapping system. Each instance of this class corresponds to a
    row in the 'hotels' table, and each class attribute represents a column.

    Attributes:
        __tablename__ (str): The name of the database table associated
                             with this model.

        id (Mapped[int]): The primary key of the hotel. A unique identifier
                          for each hotel in the system.

        title (Mapped[str]): The name or title of the hotel. Stored as a
                             string with a maximum length of 100 characters.

        location (Mapped[str]): The physical address or location of the hotel.
                                Stored as a variable-length string.
    """
    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    location: Mapped[str]
