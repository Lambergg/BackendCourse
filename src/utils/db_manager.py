from src.repositories.facilities import FacilitiesRepository, RoomsFacilitiesRepository
from src.repositories.bookings import BookingsRepository
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository
from src.repositories.users import UsersRepository


class DBManager:
    """
    Менеджер базы данных для управления сессией и репозиториями.

    Предоставляет:
    - Асинхронный контекстный менеджер.
    - Доступ к репозиториям (hotels, rooms, users и т.д.).
    - Унифицированную работу с транзакциями.

    Используется в сервисах и эндпоинтах через внедрение зависимости.

    Пример:
        async with DBManager(session_factory) as db:
            hotels = await db.hotels.get_all()
            await db.commit()
    """

    def __init__(self, session_factory):
        """
        Инициализирует менеджер с фабрикой сессий.

        Параметры:
        - session_factory: Callable,
        возвращающий новую асинхронную сессию (например, async_sessionmaker).
        """
        self.session_factory = session_factory

    async def __aenter__(self):
        """
        Создаёт новую сессию и инициализирует репозитории.

        Вызывается при входе в `async with`.

        Возвращает:
        - Себя, с готовыми репозиториями.
        """
        self.session = self.session_factory()

        # Инициализация репозиториев
        self.hotels = HotelsRepository(self.session)
        self.rooms = RoomsRepository(self.session)
        self.users = UsersRepository(self.session)
        self.bookings = BookingsRepository(self.session)
        self.facilities = FacilitiesRepository(self.session)
        self.rooms_facilities = RoomsFacilitiesRepository(self.session)

        return self

    async def __aexit__(self, *args):
        """
        Завершает сессию.

        Логика:
        - Если была ошибка — делает rollback.
        - Всегда закрывает сессию.

        Вызывается при выходе из `async with`.
        """
        await self.session.rollback()
        await self.session.aclose()

    async def commit(self):
        """
        Фиксирует текущую транзакцию.

        Должен вызываться после изменений в БД.
        """
        await self.session.commit()
