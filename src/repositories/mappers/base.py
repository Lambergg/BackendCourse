from typing import TypeVar, Type

from pydantic import BaseModel
from sqlalchemy import Row, RowMapping

from src.database import Base

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper:
    """
    Базовый класс для маппинга данных между слоями приложения.

    Назначение:
    - Преобразование ORM-объектов (из БД) в Pydantic-схемы (доменный уровень).
    - Преобразование Pydantic-схем в ORM-объекты для сохранения в БД.

    Атрибуты класса (должны быть переопределены в наследниках):
    - db_model: ORM-модель SQLAlchemy (например, `UsersOrm`, `HotelsOrm`).
    - schema: Pydantic-схема (например, `UserSchema`, `HotelSchema`).

    Используется в репозиториях для унификации преобразования данных.
    """

    db_model: Type[Base]  # ORM-модель (например, UsersOrm)
    schema: Type[SchemaType]  # Pydantic-схема (например, UserSchema)

    @classmethod
    def map_to_domain_entity(cls, data: Base | dict | Row | RowMapping) -> SchemaType:
        """
        Преобразует данные из уровня persistence (ORM, dict, Row) в доменную сущность (Pydantic-схему).

        Параметры:
        - data: Объект из БД (ORM), словарь или результат запроса (Row/RowMapping).

        Логика:
        - Использует `model_validate` с `from_attributes=True`, чтобы поддерживать:
        * ORM-объекты (например, `user.id`, `user.email`)
        * Словари
        * Результаты SQL-запросов (`Row`)

        Возвращает:
        - Экземпляр Pydantic-схемы, заполненный данными.

        Пример:
            user_orm = await session.get(UsersOrm, 1)
            user_schema = UserMapper.map_to_domain_entity(user_orm)
        """
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data: BaseModel) -> Base:
        """
        Преобразует доменную сущность (Pydantic-схему) в ORM-объект для сохранения в БД.

        Параметры:
        - data: Экземпляр Pydantic-схемы.

        Логика:
        - Извлекает все поля через `model_dump()`.
        - Создаёт и возвращает новый экземпляр ORM-модели.

        Возвращает:
        - Новый экземпляр ORM-модели, готовый к добавлению в сессию.

        Пример:
            user_schema = UserAdd(email="test@mail.ru", password="1234")
            user_orm = UserMapper.map_to_persistence_entity(user_schema)
            session.add(user_orm)
        """
        return cls.db_model(**data.model_dump())
