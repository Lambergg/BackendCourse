import logging
from typing import Sequence, Any

from asyncpg.exceptions import UniqueViolationError
import sqlalchemy.exc
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Base
from src.exceptions import ObjectNotFoundException, ObjectAlreadyExistsException
from src.repositories.mappers.base import DataMapper


class BaseRepository:
    """
    Базовый репозиторий для выполнения CRUD-операций с ORM-моделями.

    Предоставляет универсальные методы для работы с любым типом данных,
    используя паттерн Repository + Mapper.

    Атрибуты класса (должны быть переопределены в наследниках):
    - model: ORM-модель SQLAlchemy (например, `UsersOrm`, `HotelsOrm`).
    - mapper: Маппер для преобразования между ORM и Pydantic-схемой.

    Параметры:
    - session (AsyncSession): Асинхронная сессия SQLAlchemy.
    """
    model: type[Base]
    mapper: type[DataMapper]
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_filtered(self, *filter, **filter_by) -> list[BaseModel | Any]:
        """
        Возвращает список объектов, соответствующих фильтрам.

        Параметры:
        - *filter: SQL-выражения (например, `model.id > 5`).
        - **filter_by: Фильтрация по полям (например, `id=1`, `title="test"`).

        Логика:
        - Строит запрос `SELECT ... WHERE`.
        - Преобразует результаты через `mapper.map_to_domain_entity()`.

        Возвращает:
        - Список Pydantic-схем (или `Any`, если схема не указана).
        """
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs) -> list[BaseModel | Any]:
        """
        Возвращает все объекты модели.

        Является обёрткой над `get_filtered()` без фильтров.

        Возвращает:
        - Список всех объектов.
        """
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by) -> BaseModel | None | Any:
        """
        Возвращает один объект или `None`, если не найден.

        Параметры:
        - **filter_by: Фильтрация по полям.

        Логика:
        - Выполняет `SELECT ... LIMIT 1`.
        - Если объект не найден — возвращает `None`.

        Возвращает:
        - Pydantic-схему или `None`.
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        #print(query.compile(compile_kwargs={"literal_binds": True}))
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by) -> BaseModel:
        """
        Возвращает один объект. Если не найден — выбрасывает исключение.

        Параметры:
        - **filter_by: Фильтрация по полям.

        Логика:
        - Использует `scalar_one()` → ожидает ровно один результат.
        - При отсутствии или множественных результатах — ошибка.

        Исключения:
        - ObjectNotFoundException: если объект не найден.

        Возвращает:
        - Pydantic-схему.
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except sqlalchemy.exc.NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel) -> BaseModel | Any:
        """
        Добавляет новый объект в БД.

        Параметры:
        - data (BaseModel): Pydantic-схема с данными для сохранения.

        Логика:
        - Преобразует схему в ORM-объект через `model_dump()`.
        - Выполняет `INSERT ... RETURNING *`.
        - Обрабатывает дубликаты (`UniqueViolationError`).

        Исключения:
        - ObjectAlreadyExistsException: если нарушено уникальное ограничение.
        - IntegrityError: для других ошибок целостности.

        Возвращает:
        - Созданный объект как Pydantic-схему.
        """
        try:
            add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
            result = await self.session.execute(add_data_stmt)
            model = result.scalars().one()
            return self.mapper.map_to_domain_entity(model)
        except IntegrityError as ex:
            logging.error(
                f'Не удалось добавить данные в БД, входные данные: {data=}, тип ошибки: {type(ex.orig.__cause__)=}'
            )
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                raise ObjectAlreadyExistsException from ex
            else:
                logging.error(
                    f'Незнакомая ошибка. Входные данные: {data=}, тип ошибки: {type(ex.orig.__cause__)=}'
                )
                raise ex


    async def add_bulk(self, data: Sequence[BaseModel]):
        """
        Массовое добавление объектов.

        Параметры:
        - data (Sequence[BaseModel]): Список схем для вставки.

        Логика:
        - Преобразует каждую схему в словарь.
        - Выполняет `INSERT` без возврата.

        Примечание:
        - Не вызывает `RETURNING`, поэтому не возвращает созданные объекты.
        """
        add_data_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_data_stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        """
        Частичное или полное обновление объекта.

        Параметры:
        - data (BaseModel): Данные для обновления.
        - exclude_unset (bool): Если True — обновляются только переданные поля.
        - **filter_by: Условия для поиска объекта (например, id=1).

        Логика:
        - Формирует `UPDATE ... SET ... WHERE`.
        - Использует `model_dump(exclude_unset=True)` при необходимости.

        Пример:
            await repo.edit(user_schema, id=1, exclude_unset=True)
        """
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_stmt)

    async def delete(self, **filter_by) -> None:
        """
        Удаляет объект(ы) по фильтру.

        Параметры:
        - **filter_by: Условия удаления (например, id=1).

        Логика:
        - Выполняет `DELETE FROM ... WHERE`.

        Примечание:
        - Не проверяет существование объекта.
        """
        delete_stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
