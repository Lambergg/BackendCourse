from pydantic import BaseModel, Field


class HotelAdd(BaseModel):
    title: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)


class Hotel(HotelAdd):
    id: int


class HotelPatch(BaseModel):
    title: str | None = Field(None, min_length=1)
    location: str | None = Field(None, min_length=1)
