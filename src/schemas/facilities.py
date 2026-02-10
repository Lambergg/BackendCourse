from pydantic import BaseModel, ConfigDict, Field


class FacilitiesAdd(BaseModel):
    title: str = Field(..., min_length=1)


class Facilities(FacilitiesAdd):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomsFacilitiesAdd(BaseModel):
    room_id: int
    facility_id: int


class RoomsFacilities(RoomsFacilitiesAdd):
    id: int
