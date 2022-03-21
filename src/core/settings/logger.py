from .base import BaseSettings

import logging


class LoggerSettings(BaseSettings):
    LOGGING_LEVEL: int = logging.INFO
    LOGGERS: list[str] = ['uvicorn.asgi', 'uvicorn.access']


__all__ = (
    'LoggerSettings',
)
