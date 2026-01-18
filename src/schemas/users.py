from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRequestAdd(BaseModel):
    """Schema for user registration request data.

    This model is used to validate incoming user registration data
    from the client. It includes the user's email and plain-text password
    before any processing.

    Attributes:
        email (str): The user's email address.
        password (str): The user's plain-text password.
    """

    email: EmailStr
    password: str = Field(min_length=8)


class UserAdd(BaseModel):
    """Schema for user data used internally to create a new user.

    This model represents the data required to add a new user
    to the system, typically after the password has been hashed.

    Attributes:
        email (str): The user's email address.
        hashed_password (str): The hashed version of the user's password.
    """

    email: EmailStr
    hashed_password: str


class User(BaseModel):
    """Schema for user response data.

    This model is used to serialize user data when returning
    user information to the client. It includes only public
    user information such as the ID and email.

    The model is configured to work with ORM objects directly
    by allowing attribute-based data extraction.

    Attributes:
        id (int): The unique identifier of the user.
        email (str): The user's email address.
    """

    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserWithHashedPassword(User):
    hashed_password: str
