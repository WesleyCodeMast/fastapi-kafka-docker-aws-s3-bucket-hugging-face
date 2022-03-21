from .base import BaseSchema


class Error(BaseSchema):
    field: str | None = None
    detail: str | None = None
    code: str


class ErrorWrapper(BaseSchema):
    errors: list[Error] = []


__all__ = (
    'Error',
    'ErrorWrapper',
)
