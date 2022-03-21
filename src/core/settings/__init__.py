from pydantic import SecretStr, RedisDsn

from functools import lru_cache

from .database import DatabaseSettings
from .fastapi import FastAPISettings
from .logger import LoggerSettings


class Settings(DatabaseSettings, FastAPISettings, LoggerSettings):
    SECRET_KEY: SecretStr

    REDIS_URL: RedisDsn

    DEVICE_ID_SECRET_KEY: SecretStr
    DEVICE_ID_PUBLIC_KEY: SecretStr

    JWT_TOKEN_LIFETIME: int = 86400

    S3_ACCESS_KEY: str
    S3_SECRET_KEY: SecretStr
    S3_ENDPOINT_URL: str | None = None
    S3_REGION_NAME: str | None = None
    S3_STORAGE_URL: str

    OPENAI_API_KEY: str
    ADAPTY_SECRET_KEY: str

    KAFKA_SERVICE: str

    class Config:
        validate_assignment = True


@lru_cache
def get_application_settings() -> Settings:
    return Settings()


__all__ = (
    'Settings',
    'get_application_settings',
)
