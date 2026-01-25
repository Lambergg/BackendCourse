from datetime import datetime, timezone, timedelta
import jwt
from fastapi import HTTPException, Response
from passlib.context import CryptContext


from src.config import settings
from src.exceptions import ObjectAlreadyExistsException, UserNotRegisterHTTPException, \
    WrongPasswordHTTPException, UserAllReadyExistsHTTPException
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
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
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный токен")

    async def register_user(
            self,
            data: UserRequestAdd,
    ):
        hashed_password = AuthService().hash_password(data.password)
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
        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        if not user:
            raise UserNotRegisterHTTPException
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise WrongPasswordHTTPException
        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token, "token_type": "bearer"}

    async def get_me(
            self,
            user_id: int,
    ):
        user = await self.db.users.get_one_or_none(id=user_id)
        return user
