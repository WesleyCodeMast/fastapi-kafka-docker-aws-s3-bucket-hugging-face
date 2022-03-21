from fastapi import APIRouter

from media.views import router as media_router
from users.views import router as users_router
from avatars.views import router as avatars_router
from messenger.views import router as messenger_router


router = APIRouter(prefix='/v1')
router.include_router(media_router, tags=['media'], prefix='/media')
router.include_router(users_router, tags=['users'], prefix='/users')
router.include_router(avatars_router, tags=['avatars'], prefix='/avatars')
router.include_router(messenger_router, tags=['messenger'], prefix='/messages')


__all__ = (
    'router',
)
