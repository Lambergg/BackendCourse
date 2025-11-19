import asyncio
import aiohttp

async def get_data(i: int, endpoint: str):
    print(f'Начал выполнение: {i}')
    url = f'http://127.0.0.1:8080/{endpoint}/{i}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(f'Закончил выполнение: {i}')


async def main():
    await asyncio.gather(
        *[get_data(i, "sync") for i in range(300)]
    )


asyncio.run(main())

"""
import time
import asyncio
import threading


@app.get("/sync/{id}")
def sync_func(id: int):
    print(f'sync. Потоков: {threading.active_count()}')
    print(f'sync. начал {id}: {time.time():.2f}')
    time.sleep(3)
    print(f'sync. закончил {id}: {time.time():.2f}')


@app.get("/async/{id}")
async def async_func(id: int):
    print(f'async. Потоков: {threading.active_count()}')
    print(f'async. начал {id}: {time.time():.2f}')
    await asyncio.sleep(3)
    print(f'async. закончил {id}: {time.time():.2f}')
"""