from pydantic import BaseModel, ConfigDict, Field

from src.schemas.facilities import Facilities


class RoomAddRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str | None
    price: int = Field(..., ge=0)
    quantity: int = Field(..., ge=0)
    facilities_ids: list[int] = []


class RoomAdd(BaseModel):
    hotel_id: int
    title: str
    description: str | None = None
    price: int
    quantity: int


class Room(RoomAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomWithRels(Room):
    facilities: list[Facilities]


class RoomPatchRequest(BaseModel):
    title: str | None = Field(None, min_length=1)
    description: str | None = Field(None, min_length=1)
    price: int | None = Field(None, ge=0)
    quantity: int | None = Field(None, ge=0)
    facilities_ids: list[int] = []


class RoomPatch(BaseModel):
    hotel_id: int | None = None
    title: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
