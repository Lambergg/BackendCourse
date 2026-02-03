from datetime import date

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from src.database import Base


class BookingsOrm(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    date_from: Mapped[date]
    date_to: Mapped[date]
    price: Mapped[int]

    @hybrid_property
    def total_cost(self) -> int:
        """
        Вычисляемое свойство: общая стоимость бронирования.

        Рассчитывается как:
        цена за ночь × количество ночей

        Пример:
        date_from = 2026-01-01
        date_to = 2026-01-05
        price = 1000
        total_coast = 1000 × 4 = 4000

        Использование:
        - В SQLAlchemy запросах (благодаря @hybrid_property).
        - В Python-коде как обычное свойство.

        Возвращает:
        - Общую стоимость бронирования (int).
        """
        return self.price * (self.date_to - self.date_from).days
