from src.api.dependencies import get_db_manager
from src.schemas.hotels import HotelAdd


async def test_add_hotel():
    hotel_data = HotelAdd(title="Hotel 3 stars test", location="Сочи")
    async with get_db_manager() as db:
        new_hotel_data = await db.hotels.add(hotel_data)
        await db.commit()
        print(f'{new_hotel_data=}')
