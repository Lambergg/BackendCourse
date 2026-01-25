from fastapi import APIRouter, Response

from src.api.dependencies import UserIdDep, DBDep
from src.schemas.users import UserRequestAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/register")
async def register_user(
    data: UserRequestAdd,
    db: DBDep,
):
    await AuthService(db).register_user(data)
    return {"Status": "Ok"}


@router.post("/login")
async def login_user(
    data: UserRequestAdd,
    response: Response,
    db: DBDep,
):
    return await AuthService(db).login_user(data, response)


@router.get("/me")
async def get_me(
    user_id: UserIdDep,
    db: DBDep,
):
    return await AuthService(db).get_me(user_id)


@router.post("/logout")
async def logout_user(
    response: Response,
):
    response.delete_cookie("access_token")
    return {"Status": "Ok"}
