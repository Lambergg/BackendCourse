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
    return await AuthService(db).get_me(user_id)


@router.post(
    "/logout",
    summary="Выход пользователя",
    description="<h1>Выход пользователя и удаление токена из cookie</h1>"
)
async def logout_user(
    response: Response,
):
    response.delete_cookie("access_token")
    return {"Status": "Ok"}
