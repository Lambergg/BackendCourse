from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from src.database import Base


class UsersOrm(Base):
    """
    ORM-модель для таблицы 'users'.

    Представляет пользователей системы. Каждый пользователь имеет уникальный email и хешированный пароль.

    Атрибуты:
    - id: Уникальный идентификатор пользователя (первичный ключ).
    - email: Email пользователя (до 200 символов, уникальный).
    - hashed_password: Хешированный пароль (до 200 символов).

    Пример:
        user = UsersOrm(
            email="koto-pes@mail.ru",
            hashed_password="scrypt:mcf..."
        )
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
