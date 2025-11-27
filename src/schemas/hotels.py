from pydantic import BaseModel, Field


class HotelAdd(BaseModel):
    """
    Schema for adding a new hotel.

    This model is used to validate input data when creating a new hotel.
    It includes the essential fields required for hotel creation.

    Attributes:
        title (str): The name or title of the hotel.
        location (str): The physical address or location of the hotel.
    """
    title: str
    location: str


class Hotel(HotelAdd):
    """
    Schema for representing a complete hotel entity.

    This model extends HotelAdd by adding the 'id' field, making it suitable
    for representing a hotel that already exists in the database.

    Inherits:
        HotelAdd: Contains the base hotel fields (title, location).

    Attributes:
        id (int): The unique identifier of the hotel in the database.
    """
    id: int


class HotelPATCH(BaseModel):
    """
    Schema for partially updating a hotel.

    This model is used to validate input data when performing a partial
    update (PATCH request) on an existing hotel. All fields are optional
    and can be omitted if they should not be updated.

    Attributes:
        title (str | None): The new name or title of the hotel. If None, the title remains unchanged.
        location (str | None): The new physical address or location of the hotel. If None, the location remains unchanged.
    """
    title: str | None = Field(None)
    location: str | None = Field(None)
