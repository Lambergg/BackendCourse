from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilitiesAdd
from src.services.facilities import FacilityService

router = APIRouter(prefix="/facilities", tags=["Удобства"])


@router.get(
    "",
    summary="Получить список всех удобств",
    description="<h1>Возвращает список всех удобств</h1>",
)
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await FacilityService(db).get_facilities()


@router.post(
    "",
    summary="Добавить удобство",
    description="<h1>Добавляет удобство</h1>",
)
async def create_facilities(
        db: DBDep,
        facilities_data: FacilitiesAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Новое удобство",
                "value": {
                    "title": "Русская баня",
                },
            },
        }
        )
):
    facilities = await FacilityService(db).create_facility(facilities_data)
    return {"Status": "Ok", "data": facilities}
