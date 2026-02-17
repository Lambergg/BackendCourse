# ruff: noqa E402
import logging
import sys
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)


from src.api.images import router as router_images
from src.init import redis_manager
from src.api.hotels import router as router_hotels
from src.api.auth import router as router_auth
from src.api.rooms import router as router_rooms
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Асинхронный контекстный менеджер для управления жизненным циклом приложения.

    Выполняется:
    - При старте: подключается к Redis и инициализирует кэш.
    - При остановке: закрывает соединение с Redis.

    Используется через параметр `lifespan` в FastAPI.
    """
    # При старте приложения
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager._redis), prefix="fastapi-cache")
    logging.info("FasstApiCache initialized")
    yield
    # При выключении/перезагрузке приложения
    await redis_manager.close()


# Создаем экземпляр приложения FastAPI
app = FastAPI(docs_url=None, lifespan=lifespan)

# Подключение роутеров
app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_facilities)
app.include_router(router_images)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,  # type: ignore
        title=app.title + " - Swagger UI",  # type: ignore
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,  # type: ignore
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:63342/"])


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Берём первое сообщение
    error_msg = exc.errors()[0]["msg"]

    # Локализуем
    if error_msg == "Field required":
        localized_msg = "Обязательное поле"
    elif "shorter than minimum length" in error_msg:
        localized_msg = "Пароль должен быть не короче восьми символов"
    elif "value is not a valid email address" in error_msg:
        localized_msg = "Некорректный email"
    elif "String should have at least 1 character" in error_msg:
        localized_msg = "Поля должны содержать хотя бы один символ"
    elif "JSON decode error" in error_msg:
        localized_msg = "Неполные данные"
    elif "Input should be greater than or equal to 0" in error_msg:
        localized_msg = "Значение должно быть больше или равно нулю"
    elif "Input should be a valid date or datetime, input is too short" in error_msg:
        localized_msg = "Неккоректная дата"
    elif "Input should be less than or equal to 9223372036854775807" in error_msg:
        localized_msg = "Значение превышает диапазон БД"
    else:
        localized_msg = error_msg

    raise HTTPException(status_code=422, detail=localized_msg)


# Запуск сервера Uvicorn для запуска API
if __name__ == "__main__":
    """
    Точка входа для запуска приложения через Uvicorn.

    Конфигурация:
    - host: 0.0.0.0 — доступ с любого интерфейса.
    - port: 8080 — порт сервера.
    - reload: True — автоматическая перезагрузка при изменении кода (для разработки).
    """
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


"""
Если плохо работает документация OpenAPI.

from fastapi.openapi.docs import get_swagger_ui_html

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )
app = FastAPI(docs_url=None)
"""
