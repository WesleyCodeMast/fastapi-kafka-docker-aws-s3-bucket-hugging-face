from core.exceptions import APIError

from fastapi import status


class MediaNotFound(APIError):
    status_code = status.HTTP_404_NOT_FOUND
    field = 'media_id'
    detail = 'Media with specified identifier not found'
    code = 'media.not_found'


__all__ = (
    'MediaNotFound',
)
