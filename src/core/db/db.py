from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    close_all_sessions as async_close_all_sessions

from loguru import logger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

    from core.settings import Settings


_db_engine: 'AsyncEngine'
_db_session_maker: async_sessionmaker


async def get_db_session() -> 'AsyncSession':
    async with _db_session_maker() as session:
        yield session


def get_session_maker() -> 'AsyncSession':
    return _db_session_maker()


def get_session(session: 'AsyncSession' = None) -> tuple['AsyncSession', bool]:
    return (session, False) if session is not None else (get_session_maker(), True)


async def setup_database_service(settings: 'Settings') -> None:
    global _db_engine, _db_session_maker

    _db_engine = create_async_engine(str(settings.DATABASE_URL))
    _db_session_maker = async_sessionmaker(_db_engine, expire_on_commit=False)

    from sqlalchemy import text

    async with _db_session_maker() as session:
        statement = text('SELECT 1')
        await session.execute(statement)

    logger.debug('setup_database_service() attached')


async def shutdown_database_service() -> None:
    await async_close_all_sessions()
    await _db_engine.dispose()


__all__ = (
    'get_session',
    'get_db_session',
    'get_session_maker',
    'setup_database_service',
    'shutdown_database_service',
)
