from core.exceptions import APIError

from fastapi import status


class OpenAIError(APIError):
    status_code = status.HTTP_400_BAD_REQUEST
    field = 'avatar'
    detail = 'Couldn\'t get a response from the avatar'
    code = 'avatar.issue'


__all__ = (
    'OpenAIError',
)
