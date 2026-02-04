from sqlalchemy import select
from pydantic import EmailStr

from src.repositories.base import BaseRepository
from src.models.users import UsersOrm
from src.repositories.mappers.mappers import UserDataMapper
from src.schemas.users import UserWithHashedPassword


class UsersRepository(BaseRepository):
    """
    Репозиторий для работы с пользователями.

    Предоставляет методы:
    - Получение пользователя по email с хешированным паролем (для аутентификации).

    Атрибуты:
    - model: ORM-модель `UsersOrm`.
    - mapper: Маппер `UserDataMapper` для преобразования в Pydantic-схему.
    """
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr):
        """
        Возвращает пользователя по email, включая хешированный пароль.

        Параметры:
        - email (EmailStr): Email пользователя (валидируется как корректный email).

        Логика:
        - Выполняет запрос: SELECT * FROM users WHERE email = :email.
        - Ожидает ровно один результат (scalar_one).
        - Преобразует ORM-объект в схему `UserWithHashedPassword`.

        Используется в сервисе аутентификации при входе.

        Исключения:
        - sqlalchemy.exc.NoResultFound: если пользователь не найден.
        - sqlalchemy.exc.MultipleResultsFound: если найдено более одного (невозможно при unique(email)).

        Возвращает:
        - Pydantic-схему `UserWithHashedPassword`, содержащую id, email и hashed_password.
        """
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        # logger.debug("SQL: %s", query.compile(dialect=PostgreSQLDialect(), compile_kwargs={"literal_binds": True}))
        #print(query.compile(compile_kwargs={"literal_binds": True}))
        model = result.scalars().one()
        return UserWithHashedPassword.model_validate(model)
