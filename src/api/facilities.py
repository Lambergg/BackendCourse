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
    """
    Получает список всех удобств (например: Wi-Fi, бассейн, парковка и т.д.).

    Параметры:
    - db (DBDep): Зависимость для работы с базой данных.

    Логика:
    - Вызывает сервис `FacilityService(db).get_facilities()`.
    - Сервис получает все записи из таблицы `facilities`.

    Кэширование:
    - Результат кэшируется на 10 секунд через `fastapi-cache`.

    Возвращает:
    - Список всех удобств.
    """
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
    ),
):
    """
    Добавляет новое удобство (например: «Сауна», «Wi-Fi», «Бесплатная парковка»).

    Параметры:
    - db (DBDep): Зависимость для работы с БД.
    - facilities_data (FacilitiesAdd): Данные нового удобства — только `title`.

    Логика:
    1. Передаёт данные в `FacilityService.create_facility()`.
    2. Сервис проверяет, не существует ли уже удобство с таким названием.
    3. Если нет — создаёт новую запись в БД.

    Возвращает:
    - JSON: {"Status": "Ok", "data": {...}} — созданное удобство.
    """
    facilities = await FacilityService(db).create_facility(facilities_data)
    return {"Status": "Ok", "data": facilities}
