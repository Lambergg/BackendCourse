from httpx import AsyncClient


async def test_get_hotels(ac: AsyncClient):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": "2024-01-01",
            "date_to": "2024-01-07",
        }
    )

    assert response.status_code == 200
