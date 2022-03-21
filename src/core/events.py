from loguru import logger

from typing import TYPE_CHECKING

from .db import setup_database_service, shutdown_database_service
from .broadcaster import setup_broadcast_service, shutdown_broadcast_service

if TYPE_CHECKING:
    from .settings import Settings


async def on_startup_handler(settings: 'Settings') -> None:
    """ Application startup event handler """

    logger.debug('Application startup requested')

    await setup_database_service(settings)
    await setup_broadcast_service(settings)


async def on_shutdown_handler(settings: 'Settings') -> None:
    """ Application shutdown event handler """

    logger.debug('Application shutdown requested')

    await shutdown_database_service()
    await shutdown_broadcast_service(settings)


__all__ = (
    'on_startup_handler',
    'on_shutdown_handler',
)
