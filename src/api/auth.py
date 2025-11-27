from fastapi import APIRouter

from src.database import async_session_maker
from src.repositories.users import UsersRepository
from src.schemas.users import UserRequestAdd, UserAdd

router = APIRouter(prefix="/auth", tags=["Автроизация и аутентификация"])


@router.post("/register")
async def register_user(
        data: UserRequestAdd,
):
    hashed_password = "123gfhjghjty56hgj"
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
    async with async_session_maker() as session:
        await UsersRepository(session).add(new_user_data)
        await session.commit()

    return {"Status": "Ok"}
