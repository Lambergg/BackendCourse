from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class defines the environment-based configuration for the application
    using Pydantic's BaseSettings. It reads configuration values from environment
    variables or a .env file and provides computed properties for derived settings.

    Attributes:
        DB_HOST (str): The hostname or IP address of the PostgreSQL database server.
        DB_PORT (int): The port number on which the PostgreSQL database server is running.
        DB_USER (str): The username for authenticating with the PostgreSQL database.
        DB_PASS (str): The password for authenticating with the PostgreSQL database.
        DB_NAME (str): The name of the PostgreSQL database to connect to.
    """
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DB_URL(self):
        """
        Generate the database connection URL.

        This property constructs a PostgreSQL connection URL using the asyncpg
        driver with the provided database configuration settings. The URL follows
        the format: postgresql+asyncpg://user:password@host:port/database

        Returns:
            str: The complete database connection URL suitable for use with
                SQLAlchemy and asyncpg.
        """
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")
    """
    Configuration for the Settings class.

    Specifies that settings should be loaded from a .env file in the current directory.
    This allows for environment-specific configuration without hardcoding values.
    """


settings = Settings()
"""
Global instance of the Settings class.

This singleton instance loads and holds all application settings from environment
variables or the .env file. It should be imported and used throughout the application
to access configuration values.
"""