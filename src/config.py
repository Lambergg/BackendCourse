from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Класс для управления конфигурацией приложения.

    Загружает переменные окружения из файла `.env` и предоставляет удобные свойства:
    - DB_URL: Строка подключения к PostgreSQL (с использованием asyncpg).
    - REDIS_URL: Строка подключения к Redis.

    Атрибуты:
    - MODE: Режим запуска приложения. Один из: "TEST", "LOCAL", "DEV", "PROD".
    - DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME: Параметры подключения к БД.
    - REDIS_HOST, REDIS_PORT: Параметры подключения к Redis.
    - JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES: Настройки аутентификации.

    Использование:
        settings = Settings()
        db_url = settings.DB_URL
        redis_url = settings.REDIS_URL
    """

    MODE: Literal["TEST", "LOCAL", "DEV", "PROD"]

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def REDIS_URL(self):
        """
        Возвращает строку подключения к Redis.

        Пример: redis://localhost:6379
        """
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def DB_URL(self):
        """
        Возвращает строку подключения к PostgreSQL с использованием драйвера asyncpg.

        Пример: postgresql+asyncpg://user:pass@localhost:5432/dbname
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore
