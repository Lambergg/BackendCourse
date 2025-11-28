from sqlalchemy import select
from pydantic import EmailStr

from src.repositories.base import BaseRepository
from src.models.users import UsersOrm
from src.schemas.users import User, UserWithHashedPassword


class UsersRepository(BaseRepository):
    """
    Repository class for handling database operations related to the User entity.

    This class extends the BaseRepository to provide specific functionality
    for the UsersOrm model and User schema. It encapsulates all data access
    logic for user records, including creation, retrieval, updating, and deletion.

    The repository uses the BaseRepository's generic methods while specifying
    the concrete model and schema to work with, enabling type-safe operations
    and automatic serialization/deserialization between ORM objects and
    Pydantic models.

    Attributes:
    model (type[UsersOrm]): The ORM model class that this repository manages.
    Specifies that this repository works with the UsersOrm model.
    schema (type[User]): The Pydantic schema class used for data validation
    and serialization. Specifies that results should be returned as
    User schema instances.

    Example:
    async with async_session_maker() as session:
    repo = UsersRepository(session)
    user_data = UserAdd(email="user@example.com", hashed_password="...")
    await repo.add(user_data)
    user = await repo.find_one(email="user@example.com")
    """
    model = UsersOrm
    schema = User

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        model = result.scalars().one()
        return UserWithHashedPassword.model_validate(model)
