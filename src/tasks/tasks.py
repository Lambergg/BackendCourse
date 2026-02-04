import asyncio
import logging
from time import sleep
from PIL import Image
import os

from src.database import async_session_maker_null_pool
from src.tasks.celery_app import celery_instance
from src.utils.db_manager import DBManager


@celery_instance.task
def test_task():
    """
    Пример фоновой задачи, имитирующей долгую операцию.

    Выполняет:
    - Паузу на 5 секунд.
    - Логирование завершения.

    Используется для демонстрации работы Celery.
    """
    sleep(5)
    logging.info("Я закончил")


@celery_instance.task
def resize_image(image_path: str):
    """
    Асинхронно изменяет размер изображения на несколько стандартных значений.

    Параметры:
    - image_path (str): Полный путь к исходному изображению.

    Логика:
    1. Открывает изображение с помощью PIL.
    2. Создаёт версии с шириной: 1000px, 500px, 200px.
    3. Сохраняет в `src/static/images` с суффиксом `_размерpx`.

    Особенности:
    - Сохраняет пропорции изображения.
    - Использует `LANCZOS` для высококачественного ресемплинга.

    Пример выходных файлов:
        original.jpg → original_1000px.jpg, original_500px.jpg, original_200px.jpg
    """
    logging.debug(f'Вызываеться resize_image с аргументом {image_path=}')
    sizes = [1000, 500, 200]
    output_folder = "src/static/images"

    # Открываем изображение
    img = Image.open(image_path)

    # Получаем имя файла и его расширение
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)

    # Проходим по каждому размеру
    for size in sizes:
        # Сжимаем изображение
        img_resized = img.resize(
            (size, int(img.height * (size / img.width))), Image.Resampling.LANCZOS
        )

        # Формируем имя нового файла
        new_file_name = f"{name}_{size}px{ext}"

        # Полный путь для сохранения
        output_path = os.path.join(output_folder, new_file_name)

        # Сохраняем изображение
        img_resized.save(output_path)

    logging.info(f"Изображение сохранено в следующих размерах: {sizes} в папке {output_folder}")


async def get_bookings_with_today_checkin_helper():
    """
    Асинхронная функция для получения бронирований с заездом сегодня.

    Используется как вспомогательная для Celery-задачи.
    """
    logging.info("Я НАЧАЛ!")
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.bookings.get_bookings_with_today_checkin()
        logging.debug(f"{bookings=}")


@celery_instance.task(name="booking_today_checkin")
def send_emails_to_users_with_today_checkin():
    """
    Celery-задача для отправки уведомлений пользователям с заездом сегодня.

    Поскольку Celery работает в синхронном режиме, используется `asyncio.run()`
    для запуска асинхронного кода.

    Логика:
    - Запускает `get_bookings_with_today_checkin_helper()`.
    - В будущем — можно добавить отправку email/SMS.

    Запускается по расписанию (через Celery Beat).
    """
    asyncio.run(get_bookings_with_today_checkin_helper())
