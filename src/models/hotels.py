from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, BigInteger

from src.database import Base


class HotelsOrm(Base):
    """
    ORM-модель для таблицы 'hotels'.

    Представляет отели в системе бронирования.

    Атрибуты:
    - id: Уникальный идентификатор отеля (первичный ключ).
    - title: Название отеля (до 100 символов).
    - location: Адрес или местоположение отеля.

    Пример:
        hotel = HotelsOrm(
            title="Отель Сочи у моря",
            location="ул. Морская, д. 10"
        )
    """

    __tablename__ = "hotels"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    location: Mapped[str]
