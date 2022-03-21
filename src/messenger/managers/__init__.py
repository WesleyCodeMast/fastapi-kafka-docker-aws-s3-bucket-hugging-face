from .connection import ConnectionManager

from functools import lru_cache


@lru_cache
def get_connection_manager() -> 'ConnectionManager':
    return ConnectionManager()


__all__ = (
    'ConnectionManager',
    'get_connection_manager',
)
