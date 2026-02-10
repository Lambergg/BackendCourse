import typing

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, BigInteger, String

from src.database import Base

if typing.TYPE_CHECKING:
    from src.models import FacilitiesOrm


class RoomsOrm(Base):
    """
    ORM-модель для таблицы 'rooms'.

    Представляет номера в отелях. Каждый номер принадлежит одному отелю и может иметь несколько удобств.

    Атрибуты:
    - id: Уникальный идентификатор номера (первичный ключ).
    - hotel_id: Ссылка на отель (внешний ключ к `hotels.id`).
    - title: Название номера (например: "Люкс", "Стандарт").
    - description: Описание номера (опционально).
    - price: Цена за одну ночь.
    - quantity: Количество доступных номеров одного типа.
    - facilities: Связь "многие ко многим" с удобствами через ассоциативную таблицу `rooms_facilities`.

    Пример:
        room = RoomsOrm(
            title="VIP 101",
            description="Просторный номер с видом на море",
            price=5000,
            quantity=3,
            hotel_id=1
        )
    """

    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None]
    price: Mapped[int]
    quantity: Mapped[int]

    facilities: Mapped[list["FacilitiesOrm"]] = relationship(
        back_populates="rooms",
        secondary="rooms_facilities",
    )
