import logging

import redis.asyncio as redis


class RedisManager:
    """
    Менеджер для асинхронного подключения и работы с Redis.

    Позволяет:
    - Подключаться к Redis.
    - Выполнять базовые операции: set, get, delete.
    - Управлять временем жизни ключей (TTL).
    - Корректно закрывать соединение.

    Используется в FastAPI-приложении как зависимость или отдельный сервис.
    """

    _redis: redis.Redis

    def __init__(self, host: str, port: int):
        """
        Инициализация менеджера Redis.

        Параметры:
        - host (str): Адрес сервера Redis (например, 'localhost').
        - port (int): Порт Redis (по умолчанию 6379).
        """
        self.host = host
        self.port = port

    async def connect(self):
        """
        Устанавливает асинхронное соединение с Redis.

        Логирует начало и успешное подключение.

        Выбрасывает исключение при ошибке подключения.
        """
        logging.info("Начинаем подключение к Redis")
        self._redis = await redis.Redis(host=self.host, port=self.port)
        logging.info("Успешное подключение к Redis")

    async def set(self, key: str, value: str, expire: int | None = None):
        """
        Сохраняет значение по ключу в Redis.

        Параметры:
        - key (str): Ключ.
        - value (str): Значение.
        - expire (int | None): Время жизни ключа в секундах. Если None — без TTL.
        """
        if expire:
            await self._redis.set(key, value, ex=expire)
        else:
            await self._redis.set(key, value)

    async def get(self, key: str):
        """
        Получает значение по ключу.

        Параметры:
        - key (str): Ключ.

        Возвращает:
        - Значение в виде `bytes` или `None`, если ключ не найден.
        """
        return await self._redis.get(key)

    async def delete(self, key: str):
        """
        Удаляет ключ из Redis.

        Параметры:
        - key (str): Ключ для удаления.
        """
        await self._redis.delete(key)

    async def close(self):
        """
        Закрывает соединение с Redis.

        Проверяет, инициализировано ли соединение.
        """
        if self._redis:
            await self._redis.close()


# Пример использования:
# redis_manager = RedisManager(redis_url="redis://localhost")
# await redis_manager.connect()
# await redis_manager.set("key", "value", expire=60)
# value = await redis_manager.get("key")
# await redis_manager.delete("key")
# await redis_manager.close()
