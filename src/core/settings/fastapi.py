from .base import BaseSettings


class FastAPISettings(BaseSettings):
    DEBUG: bool = False
    ALLOWED_HOSTS: list[str] = ['*']

    DOCS_URL: str = '/docs'
    OPENAPI_PREFIX: str = ''
    OPENAPI_URL: str = '/openapi.json'
    REDOC_URL: str = '/redoc'

    API_PREFIX: str = '/api'

    TITLE: str = 'AI GF Backend'
    VERSION: str = '1.0.0'

    @property
    def fastapi_settings(self) -> dict[str, any]:
        return {
            'debug': self.DEBUG,
            'docs_url': self.DOCS_URL if self.DEBUG else None,
            'openapi_prefix': self.OPENAPI_PREFIX if self.DEBUG else None,
            'openapi_url': self.OPENAPI_URL if self.DEBUG else None,
            'redoc_url': self.REDOC_URL if self.DEBUG else None,
            'title': self.TITLE,
            'version': self.VERSION,
        }


__all__ = (
    'FastAPISettings',
)
