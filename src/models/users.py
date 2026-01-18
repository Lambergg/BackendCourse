from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.database import Base


class UsersOrm(Base):
    """
    ORM model representing the 'users' table in the database.

    This class defines the structure of the 'users' table using SQLAlchemy's
    declarative mapping system. Each instance of this class corresponds to a
    row in the 'users' table, and each class attribute represents a column.

    Attributes:
        __tablename__ (str): The name of the database table associated
            with this model.

        id (Mapped[int]): The primary key of the user. A unique identifier
            for each user in the system.

        email (Mapped[str]): The email address of the user. Stored as a
            string with a maximum length of 200 characters.

        hashed_password (Mapped[str]): The hashed version of the user's password.
            Stored as a string with a maximum length
            of 200 characters. The plain-text password
            is never stored.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
