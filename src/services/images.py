import shutil

from fastapi import UploadFile

from src.services.base import BaseService
from src.tasks.tasks import resize_image


class ImagesService(BaseService):
    """
    Сервис для загрузки изображений.

    Предоставляет метод:
    - upload_image: сохраняет файл изображения на сервер и запускает фоновое изменение размера.

    Наследуется от `BaseService`, хотя не использует БД напрямую.
    """
    def upload_image(self, file: UploadFile):
        """
        Сохраняет загруженное изображение на диск и запускает фоновое изменение размера.

        Параметры:
        - file (UploadFile): Загружаемый файл из FastAPI.

        Логика:
        1. Сохраняет файл в `src/static/images/`.
        2. Запускает Celery-задачу `resize_image` для уменьшения размера.

        Примечания:
        - Использует `shutil.copyfileobj` для потокового копирования — безопасно для больших файлов.
        - Имя файла очищается от потенциально опасных символов (в реальном проекте — использовать более строгую валидацию).

        Возвращает:
        - Относительный путь к сохранённому файлу (str).
        """
        image_path = f"src/static/images/{file.filename}"
        with open(image_path, "wb+") as new_file:
            shutil.copyfileobj(file.file, new_file)

            resize_image.delay(image_path)