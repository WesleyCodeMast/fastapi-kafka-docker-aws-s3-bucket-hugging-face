from broadcaster import Broadcast

from core.settings import get_application_settings

from loguru import logger

from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.settings import Settings


@lru_cache
def get_broadcast() -> Broadcast:
    settings = get_application_settings()
    return Broadcast(str(settings.REDIS_URL))


async def setup_broadcast_service(_) -> None:
    broadcast = get_broadcast()
    await broadcast.connect()

    logger.debug('setup_broadcast_service() attached')


async def shutdown_broadcast_service(_) -> None:
    broadcast = get_broadcast()
    await broadcast.disconnect()


__all__ = (
    'get_broadcast',
    'setup_broadcast_service',
    'shutdown_broadcast_service',
)
