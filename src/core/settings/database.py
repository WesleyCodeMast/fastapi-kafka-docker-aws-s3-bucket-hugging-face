from pydantic import PostgresDsn

from .base import BaseSettings


class DatabaseSettings(BaseSettings):
    DATABASE_URL: PostgresDsn

    MIN_CONNECTION_COUNT: int = 10
    MAX_CONNECTION_COUNT: int = 10


__all__ = (
    'DatabaseSettings',
)
