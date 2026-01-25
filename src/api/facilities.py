from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilitiesAdd
from src.services.facilities import FacilityService

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("")
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await FacilityService(db).get_facilities()


@router.post("")
async def create_facilities(db: DBDep, facilities_data: FacilitiesAdd = Body()):
    facilities = await FacilityService(db).create_facility(facilities_data)
    return {"Status": "Ok", "data": facilities}
