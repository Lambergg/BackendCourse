from fastapi import APIRouter, Body
import json

from src.api.dependencies import DBDep
from src.init import redis_manager
from src.schemas.facilities import FacilitiesAdd

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get("")
async def get_facilities(
        db: DBDep
):
    facilities_from_cache = await redis_manager.get("facilities")
    print(f"{facilities_from_cache=}")
    if not facilities_from_cache:
        print("Иду в базу")
        facilities = await db.facilities.get_all()
        facilities_schemas: list[dict] = [f.model_dump() for f in facilities]
        facilities_json = json.dumps(facilities_schemas)
        await redis_manager.set("facilities", facilities_json, 10)

        return facilities
    else:
        facilities_dicts = json.loads(facilities_from_cache)
        return facilities_dicts


@router.post("")
async def create_facilities(
        db: DBDep,
        facilities_data: FacilitiesAdd = Body()
):
    facilities = await db.facilities.add(facilities_data)
    await db.commit()

    return {"Status": "Ok", "data": facilities}
