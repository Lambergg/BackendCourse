from fastapi import APIRouter, Response, Body

from src.api.dependencies import UserIdDep, DBDep
from src.schemas.users import UserRequestAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post(
    "/register",
    summary="Регистрация нового пользователя",
    description="<h1>Для регистрации нового пользователя нужно передать email и пароль</h1>"
)
async def register_user(
    db: DBDep,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Новый пользователь",
                "value": {
                    "email": "koto-pes@mail.ru",
                    "password": "abcd1234",
                },
            }
        }
    ),
):
    """
    Эндпоинт для регистрации нового пользователя.

    Параметры:
    - `db`: Зависимость для работы с базой данных (инъекция через DI).
    - `data`: Данные пользователя (email и пароль) в теле запроса.

    Логика:
    - Передаёт данные в сервис `AuthService` для обработки.
    - Если пользователь уже существует — выбрасывается исключение.
    - Иначе — создаётся новый пользователь.

    Возвращает:
    - JSON: `{"Status": "Ok"}`
    """
    await AuthService(db).register_user(data)
    return {"Status": "Ok"}


@router.post(
    "/login",
    summary="Авторизация пользователя",
    description="<h1>Для авторизации пользователя нужно передать email и пароль</h1>"
)
async def login_user(
    response: Response,
    db: DBDep,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Пользователь",
                "value": {
                    "email": "koto-pes@mail.ru",
                    "password": "abcd1234",
                },
            }
        }
    ),
):
    """
    Эндпоинт для входа пользователя в систему.

    Параметры:
    - `response`: Объект HTTP-ответа (для установки cookie).
    - `db`: Зависимость для работы с БД.
    - `data`: Email и пароль из тела запроса.

    Логика:
    - Проверяет существование пользователя и корректность пароля.
    - При успехе: генерирует JWT-токен и устанавливает его в `access_token` (cookie).
    - Возвращает токен и тип (`bearer`) в теле ответа.

    Возвращает:
    - JSON: `{"access_token": "xxx", "token_type": "bearer"}`
    """
    return await AuthService(db).login_user(data, response)


@router.get(
    "/me",
    summary="Получение информации о пользователе",
    description="<h1>Для получения информации о пользователе он должен быть аутентифицирован</h1>"
)
async def get_me(
    user_id: UserIdDep,
    db: DBDep,
):
    """
    Эндпоинт для получения данных текущего пользователя.

    Параметры:
    - `user_id`: Зависимость, извлекающая ID пользователя из JWT-токена.
    - `db`: Зависимость для работы с БД.

    Логика:
    - Получает пользователя по `id`.
    - Если не найден — выбрасывает исключение.

    Возвращает:
    - Данные пользователя (без пароля и хеша).
    """
    return await AuthService(db).get_me(user_id)


@router.post(
    "/logout",
    summary="Выход пользователя",
    description="<h1>Выход пользователя и удаление токена из cookie</h1>"
)
async def logout_user(
    response: Response,
):
    """
    Эндпоинт для выхода из системы.

    Параметры:
    - `response`: Объект HTTP-ответа.

    Логика:
    - Удаляет cookie `access_token`.

    Возвращает:
    - JSON: `{"Status": "Ok"}`
    """
    response.delete_cookie("access_token")
    return {"Status": "Ok"}
