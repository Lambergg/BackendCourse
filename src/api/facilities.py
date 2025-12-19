from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilitiesAdd

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("")
@cache(expire=10)
async def get_facilities(
        db: DBDep
):
    print("Иду в базу")
    return await db.facilities.get_all()


@router.post("")
async def create_facilities(
        db: DBDep,
        facilities_data: FacilitiesAdd = Body()
):
    facilities = await db.facilities.add(facilities_data)
    await db.commit()

    return {"Status": "Ok", "data": facilities}
