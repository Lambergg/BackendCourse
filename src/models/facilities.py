import typing

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if typing.TYPE_CHECKING:
    from src.models import RoomsOrm


class FacilitiesOrm(Base):
    """
    ORM-модель для таблицы 'facilities'.

    Представляет удобства, доступные в номерах отелей (например: Wi-Fi, бассейн, сауна и т.д.).

    Атрибуты:
    - id: Уникальный идентификатор удобства.
    - title: Название удобства (максимум 100 символов).
    - rooms: Связь "многие ко многим" с `RoomsOrm` через ассоциативную таблицу `rooms_facilities`.

    Пример:
    facility = FacilitiesOrm(title="Wi-Fi")
    """
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)

    rooms: Mapped[list["RoomsOrm"]] = relationship(
        back_populates="facilities",
        secondary="rooms_facilities",
    )


class RoomsFacilitiesOrm(Base):
    """
    Ассоциативная ORM-модель для связи "многие ко многим" между номерами и удобствами.

    Таблица: `rooms_facilities`

    Атрибуты:
    - id: Первичный ключ.
    - room_id: Внешний ключ на `rooms.id`.
    - facility_id: Внешний ключ на `facilities.id`.

    Эта модель не используется напрямую — SQLAlchemy управляет ею автоматически через relationship.
    """
    __tablename__ = "rooms_facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
