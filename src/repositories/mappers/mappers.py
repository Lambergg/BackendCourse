from src.models.bookings import BookingsOrm
from src.models.facilities import FacilitiesOrm
from src.models.hotels import HotelsOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.bookings import Booking
from src.schemas.facilities import Facilities
from src.schemas.hotels import Hotel
from src.schemas.rooms import Room, RoomWithRels
from src.schemas.users import User


class HotelDataMapper(DataMapper):
    """
    Маппер для преобразования данных между ORM-моделью `HotelsOrm` и Pydantic-схемой `Hotel`.

    Используется в репозиториях отелей для:
    - Преобразования ORM → схема (для ответа API)
    - Схема → ORM (для сохранения в БД)
    """
    db_model = HotelsOrm
    schema = Hotel


class RoomDataMapper(DataMapper):
    """
    Маппер для преобразования данных между `RoomsOrm` и `Room`.

    Используется для базовых операций с номерами.
    """
    db_model = RoomsOrm
    schema = Room


class RoomDataWithRelsMapper(DataMapper):
    """
    Маппер для преобразования данных между `RoomsOrm` и `RoomWithRels`.

    Отличие от `RoomDataMapper`:
    - `RoomWithRels` включает связанные данные (например, удобства).
    - Используется при получении номера с дополнительной информацией.
    """
    db_model = RoomsOrm
    schema = RoomWithRels


class UserDataMapper(DataMapper):
    """
    Маппер для преобразования данных между `UsersOrm` и `User`.

    Используется в аутентификации и профиле пользователя.
    """
    db_model = UsersOrm
    schema = User


class BookingDataMapper(DataMapper):
    """
    Маппер для преобразования данных между `BookingsOrm` и `Booking`.

    Используется в сервисах бронирования.
    """
    db_model = BookingsOrm
    schema = Booking


class FacilityDataMapper(DataMapper):
    """
    Маппер для преобразования данных между `FacilitiesOrm` и `Facilities`.

    Используется при управлении удобствами отелей.
    """
    db_model = FacilitiesOrm
    schema = Facilities
