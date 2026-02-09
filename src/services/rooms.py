from datetime import date

from src.exceptions import check_date_to_after_date_from, ObjectNotFoundException, HotelNotFoundException, \
    RoomNotFoundException, HotelIndexWrongHTTPException, RoomIndexWrongHTTPException, RoomAlreadyExistsHTTPException, \
    HotelNotFoundHTTPException, RoomNotFoundHTTPException, FacilitiesNotFoundHTTPException
from src.schemas.facilities import RoomsFacilitiesAdd
from src.schemas.rooms import RoomAddRequest, Room, RoomAdd, RoomPatchRequest, RoomPatch
from src.services.base import BaseService
from src.services.hotels import HotelService


class RoomService(BaseService):
    """
    Сервис для управления номерами отелей.

    Предоставляет методы:
    - Получение номеров с фильтрацией по доступности.
    - Создание, обновление, удаление и частичное редактирование номеров.
    - Проверка существования отеля и номера перед операциями.

    Наследуется от `BaseService`, имеет доступ к `self.db` (DBManager).
    """

    async def is_room_title_taken(self, hotel_id: int, title: str) -> bool:
        """
        Проверяет, занято ли название номера в указанном отеле.

        Параметры:
        - hotel_id (int): ID отеля.
        - title (str): Название номера.

        Возвращает:
        - bool: True, если уже есть номер с таким названием.
        """
        room = await self.db.rooms.get_by_title_in_hotel(hotel_id, title)
        return room is not None

    async def get_filtered_by_time(
            self,
            hotel_id: int,
            date_from: date,
            date_to: date,
    ) -> list[Room]:
        """
        Возвращает список доступных номеров в указанном отеле и периоде.

        Параметры:
        - hotel_id (int): ID отеля.
        - date_from (date): Дата заезда.
        - date_to (date): Дата выезда.

        Логика:
        1. Проверяет, что date_from < date_to.
        2. Передаёт данные в репозиторий `rooms.get_filtered_by_time()`.

        Возвращает:
        - Список Pydantic-схем `RoomWithRels` (с удобствами).
        """
        if hotel_id <= 0:
            raise HotelIndexWrongHTTPException

        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException

        check_date_to_after_date_from(date_from, date_to)
        return await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )

    async def get_room(
            self,
            hotel_id: int,
            room_id: int,
    ):
        """
        Возвращает один номер с удобствами.

        Параметры:
        - hotel_id (int): ID отеля.
        - room_id (int): ID номера.

        Логика:
        - Вызывает `get_one_with_rels()` → загружает номер и его удобства.

        Возвращает:
        - Pydantic-схему `RoomWithRels`.
        """
        if hotel_id <= 0:
            raise HotelIndexWrongHTTPException
        elif room_id <= 0:
            raise RoomIndexWrongHTTPException

            # Сначала проверяем, существует ли отель
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundHTTPException

        # Теперь ищем номер, который принадлежит именно этому отелю
        room = await self.db.rooms.get_one_with_rels(id=room_id, hotel_id=hotel_id)
        if not room:
            raise RoomNotFoundHTTPException

        return room
        #return await self.db.rooms.get_one_with_rels(id=room_id, hotel_id=hotel_id)

    async def create_room(
            self,
            hotel_id: int,
            room_data: RoomAddRequest,
    ):
        """
        Создаёт новый номер в указанном отеле.

        Параметры:
        - hotel_id (int): ID отеля.
        - room_data (RoomAddRequest): Данные номера — название, цена, количество, удобства.

        Логика:
        1. Проверяет существование отеля.
        2. Создаёт номер через `rooms.add()`.
        3. Привязывает удобства через `rooms_facilities.add_bulk()`.
        4. Фиксирует транзакцию.

        Исключения:
        - HotelNotFoundException: если отель не существует.

        Возвращает:
        - Созданный номер как Pydantic-схему.
        """
        if hotel_id <= 0:
            raise HotelIndexWrongHTTPException
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException as ex:
            raise HotelNotFoundException from ex

        # Защита от дублирования по названию
        if await self.is_room_title_taken(hotel_id, room_data.title):
            raise RoomAlreadyExistsHTTPException

        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        room: Room = await self.db.rooms.add(_room_data)

        # Проверка существования всех удобств
        if room_data.facilities_ids:
            existing_facilities = await self.db.facilities.get_many_by_ids(room_data.facilities_ids)
            existing_ids = {f.id for f in existing_facilities}
            missing_ids = set(room_data.facilities_ids) - existing_ids

            if missing_ids:
                raise FacilitiesNotFoundHTTPException

        rooms_facilities_data = [
            RoomsFacilitiesAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids
        ]
        if rooms_facilities_data:
            await self.db.rooms_facilities.add_bulk(rooms_facilities_data)
        await self.db.commit()

    async def edit_room(
            self,
            hotel_id: int,
            room_id: int,
            room_data: RoomAddRequest,
    ):
        """
        Полностью обновляет номер.

        Параметры:
        - hotel_id (int): ID отеля.
        - room_id (int): ID номера.
        - room_data (RoomAddRequest): Новые данные номера.

        Логика:
        1. Проверяет существование отеля и номера.
        2. Обновляет основные поля.
        3. Синхронизирует удобства через `set_room_facilities()`.
        4. Фиксирует изменения.

        Возвращает:
        - None.
        """
        if hotel_id <= 0:
            raise HotelIndexWrongHTTPException
        elif room_id <= 0:
            raise RoomIndexWrongHTTPException

            # Сначала проверяем, существует ли отель
        try:
            await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundHTTPException

        # Сначала проверяем, существует ли отель
        try:
            await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundHTTPException

        # Проверка существования всех удобств
        if room_data.facilities_ids:
            existing_facilities = await self.db.facilities.get_many_by_ids(room_data.facilities_ids)
            existing_ids = {f.id for f in existing_facilities}
            missing_ids = set(room_data.facilities_ids) - existing_ids

            if missing_ids:
                raise FacilitiesNotFoundHTTPException

        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)
        _room_data = RoomAdd(hotel_id=hotel_id, **room_data.model_dump())
        await self.db.rooms.edit(_room_data, id=room_id)
        await self.db.rooms_facilities.set_room_facilities(room_id, facilities_ids=room_data.facilities_ids)
        await self.db.commit()

    async def partially_edit_room(
            self,
            hotel_id: int,
            room_id: int,
            room_data: RoomPatchRequest
    ):
        """
        Частично обновляет номер.

        Параметры:
        - hotel_id (int): ID отеля.
        - room_id (int): ID номера.
        - room_data (RoomPatchRequest): Поля для обновления.

        Логика:
        1. Проверяет существование отеля и номера.
        2. Обновляет только переданные поля (`exclude_unset=True`).
        3. Если переданы `facilities_ids` — синхронизирует связи.
        4. Фиксирует изменения.

        Возвращает:
        - None.
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)
        _room_data_dict = room_data.model_dump(exclude_unset=True)
        _room_data = RoomPatch(hotel_id=hotel_id, **_room_data_dict)
        await self.db.rooms.edit(_room_data, hotel_id=hotel_id, exclude_unset=True, id=room_id)
        if "facilities_ids" in _room_data_dict:
            await self.db.rooms_facilities.set_room_facilities(
                room_id, facilities_ids=_room_data_dict["facilities_ids"]
            )
        await self.db.commit()

    async def delete_room(
            self,
            hotel_id: int,
            room_id: int,
    ):
        """
        Удаляет номер.

        Параметры:
        - hotel_id (int): ID отеля.
        - room_id (int): ID номера.

        Логика:
        1. Проверяет существование отеля и номера.
        2. Удаляет запись из `rooms`.
        3. Автоматически удаляются связи (ON DELETE CASCADE).

        Возвращает:
        - None.
        """
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)
        await self.db.rooms.delete(id=room_id, hotel_id=hotel_id)
        await self.db.commit()

    async def get_room_with_check(self, room_id: int) -> Room:
        """
        Возвращает номер с проверкой на существование.

        Параметры:
        - room_id (int): ID номера.

        Логика:
        - Пытается получить номер.
        - Если не найден — выбрасывает `RoomNotFoundException`.

        Исключения:
        - RoomNotFoundException: если номер не существует.

        Возвращает:
        - Pydantic-схему `Room`.
        """
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException
