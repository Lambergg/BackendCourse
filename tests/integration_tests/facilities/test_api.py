async def test_get_facilities(ac):
    response = await ac.get("/facilities")

    assert response.status_code == 200


async def test_add_facilities(ac):
    response = await ac.get(
        "/facilities",
        params={
            "title": "Удобство в номере"
        }
    )

    assert response.status_code == 200
