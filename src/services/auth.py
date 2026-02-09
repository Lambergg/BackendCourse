from datetime import datetime, timezone, timedelta
import jwt
from fastapi import HTTPException, Response
from passlib.context import CryptContext


from src.config import settings
from src.exceptions import ObjectAlreadyExistsException, UserNotRegisterHTTPException, \
    WrongPasswordHTTPException, UserAllReadyExistsHTTPException, UserPasswordToShortHTTPException
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.base import BaseService


class AuthService(BaseService):
    """
    Сервис для управления аутентификацией пользователей.

    Реализует:
    - Хеширование паролей.
    - Создание и проверку JWT-токенов.
    - Регистрацию, вход и получение профиля пользователя.

    Наследуется от `BaseService`, имеет доступ к `self.db` (сессия БД).
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    """
    Контекст для хеширования паролей с использованием bcrypt.
    Поддерживает устаревшие схемы автоматически.
    """

    def create_access_token(self, data: dict) -> str:
        """
        Создаёт JWT-токен с заданными данными и временем жизни.

        Параметры:
        - data (dict): Данные для включения в токен (например, {"user_id": 1}).

        Логика:
        - Копирует входные данные.
        - Добавляет `exp` (время истечения) — сейчас + ACCESS_TOKEN_EXPIRE_MINUTES.
        - Кодирует токен с помощью `JWT_SECRET_KEY` и `JWT_ALGORITHM`.

        Возвращает:
        - Закодированный JWT-токен (str).
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        """
        Хеширует пароль с использованием bcrypt.

        Параметры:
        - password (str): Открытый пароль.

        Возвращает:
        - Хеш пароля (str).
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        """
        Проверяет, соответствует ли открытый пароль хешированному.

        Параметры:
        - plain_password (str): Пароль из формы входа.
        - hashed_password (str): Хеш из БД.

        Возвращает:
        - True, если пароли совпадают, иначе False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def decode_token(self, token: str) -> dict:
        """
        Декодирует JWT-токен и возвращает его содержимое.

        Параметры:
        - token (str): JWT-токен из куки или заголовка.

        Логика:
        - Декодирует токен с помощью секретного ключа.
        - Проверяет подпись и срок действия.

        Исключения:
        - HTTPException(401): если токен недействителен или повреждён.

        Возвращает:
        - Payload токена (dict), например: {"user_id": 1, "exp": ...}.
        """
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный токен")

    async def register_user(
            self,
            data: UserRequestAdd,
    ):
        """
        Регистрирует нового пользователя.

        Параметры:
        - data (UserRequestAdd): Данные пользователя — email и пароль.

        Логика:
        1. Хеширует пароль.
        2. Создаёт схему `UserAdd` для сохранения в БД.
        3. Пытается добавить пользователя через репозиторий.
        4. Если email уже существует — выбрасывает исключение.

        Исключения:
        - UserAllReadyExistsHTTPException: если пользователь уже есть.

        Возвращает:
        - None.
        """
        if len(data.password) < 8:
            raise UserPasswordToShortHTTPException
        hashed_password = self.hash_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        try:
            await self.db.users.add(new_user_data)
            await self.db.commit()
        except ObjectAlreadyExistsException:
            raise UserAllReadyExistsHTTPException

    async def login_user(
            self,
            data: UserRequestAdd,
            response: Response,
    ):
        """
        Аутентифицирует пользователя и выдаёт JWT-токен.

        Параметры:
        - data (UserRequestAdd): Email и пароль.
        - response (Response): Для установки куки.

        Логика:
        1. Ищет пользователя по email (включая хеш пароля).
        2. Если не найден — ошибка "пользователь не зарегистрирован".
        3. Проверяет пароль.
        4. Если пароль неверный — ошибка.
        5. Создаёт токен и устанавливает его в куки.

        Исключения:
        - UserNotRegisterHTTPException: если пользователь не найден.
        - WrongPasswordHTTPException: если пароль не совпадает.

        Возвращает:
        - JSON: {"access_token": "...", "token_type": "bearer"}.
        """
        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        if not user:
            raise UserNotRegisterHTTPException
        if not self.verify_password(data.password, user.hashed_password):
            raise WrongPasswordHTTPException
        access_token = self.create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_me(
            self,
            user_id: int,
    ):
        """
        Возвращает данные текущего пользователя.

        Параметры:
        - user_id (int): ID пользователя из токена.

        Логика:
        - Получает пользователя по ID.
        - Не возвращает хеш пароля (используется схема без него).

        Возвращает:
        - Pydantic-схему пользователя (без hashed_password).
        """
        user = await self.db.users.get_one_or_none(id=user_id)
        return user
