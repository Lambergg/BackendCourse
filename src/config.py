from pydantic import BaseModel
from dotenv import load_dotenv
import os


load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")


class Settings(BaseModel):
    DB_HOST: str = DB_HOST
    DB_PORT: int = DB_PORT
    DB_USER: str = DB_USER
    DB_PASS: str = DB_PASS
    DB_NAME: str = DB_NAME

    @property
    def DB_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


settings = Settings()
