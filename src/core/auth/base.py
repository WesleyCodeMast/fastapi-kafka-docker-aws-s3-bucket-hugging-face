from fastapi import WebSocket, WebSocketException
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from starlette.status import HTTP_401_UNAUTHORIZED

from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy

from core.settings import get_application_settings

from functools import lru_cache
from typing import Optional


class WSOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, websocket: WebSocket) -> Optional[str]:
        authorization = websocket.headers.get('Authorization')
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != 'bearer':
            if self.auto_error:
                raise WebSocketException(
                    code=HTTP_401_UNAUTHORIZED,
                    reason='Not authenticated',
                )
            else:
                return None
        return param


class WSBearerTransport(BearerTransport):
    scheme: WSOAuth2PasswordBearer

    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl)
        self.scheme = WSOAuth2PasswordBearer(tokenUrl, auto_error=False)


bearer_transport = BearerTransport(tokenUrl='api/v1/users/oauth2')
ws_bearer_transport = WSBearerTransport(tokenUrl='api/v1/users/oauth2')


@lru_cache
def get_jwt_strategy() -> JWTStrategy:
    settings = get_application_settings()
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=settings.JWT_TOKEN_LIFETIME)


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


ws_auth_backend = AuthenticationBackend(
    name='jwt',
    transport=ws_bearer_transport,
    get_strategy=get_jwt_strategy,
)


__all__ = (
    'auth_backend',
    'ws_auth_backend',
)
