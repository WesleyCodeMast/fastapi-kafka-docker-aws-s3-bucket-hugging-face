from .base import BaseSchema


class StatusSchema(BaseSchema):
    status: bool


__all__ = (
    'StatusSchema',
)
