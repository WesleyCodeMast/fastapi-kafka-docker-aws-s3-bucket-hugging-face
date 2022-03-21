from fastapi import APIRouter

from .schemas import MediaSchema
from .services import get_media_by_id
from .exceptions import MediaNotFound

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Media


router = APIRouter()


@router.get('/{media_id}', response_model=MediaSchema)
async def get_media_view(media_id: int) -> 'Media':
    """ The endpoint for receiving media content """

    media = await get_media_by_id(media_id)

    if not media:
        raise MediaNotFound()

    return media


__all__ = (
    'router',
)
