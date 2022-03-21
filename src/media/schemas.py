from core.schemas import BaseSchema


class MediaSchema(BaseSchema):
    """ The scheme of media content """

    id: int
    name: str
    url: str


__all__ = (
    'MediaSchema',
)
