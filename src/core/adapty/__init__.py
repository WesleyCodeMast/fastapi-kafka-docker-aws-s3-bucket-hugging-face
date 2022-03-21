from .client import AdaptyClient

from ..settings import get_application_settings

from functools import lru_cache


@lru_cache
def get_adapty_client() -> AdaptyClient:
    settings = get_application_settings()

    return AdaptyClient(secret_key=settings.ADAPTY_SECRET_KEY)


__all__ = (
    'AdaptyClient',
    'get_adapty_client',
)
