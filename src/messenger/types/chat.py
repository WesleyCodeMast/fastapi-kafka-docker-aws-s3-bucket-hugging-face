from core.schemas import BaseSchema

from media.schemas import MediaSchema


class ChatSchema(BaseSchema):
    """ The chat scheme (for the interlocutor) """

    id: int
    name: str
    is_online: bool
    is_avatar: bool
    photo: MediaSchema | None


__all__ = (
    'ChatSchema',
)
