import time

from pydantic_settings import BaseSettings
from utils.logger import logger


class Settings(BaseSettings):
    ENV: str = "development"
    ADMIN_PWD: str = ""
    API_PREFIX: str = "/api/v1"
    DATABASE_ECHO: bool = False
    DATABASE_MAX_OVERFLOW: int = 64
    POSTGRES_DB_URI: str = ""
    POSTGRES_DB_URI_SYNC: str = ""
    REDIS_URI: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 2  # 8 hour
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    SECRET_KEY: str = ""  # used for JWT token signing

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


st = time.time()
settings = Settings()
logger.info(f"Settings loaded in {time.time() - st:.2f} seconds")
