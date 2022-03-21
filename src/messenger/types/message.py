from core.schemas import BaseSchema

from media.schemas import MediaSchema

from .chat import ChatSchema
from .role import Role

from datetime import datetime


class MessageSchema(BaseSchema):
    """ The scheme for the message """

    id: int
    text: str | None
    photo: MediaSchema | None
    unread_mark: bool
    limit_daily_image: bool = False
    created_at: datetime
    from_user: ChatSchema


class AssistantMessageSchema(BaseSchema):
    """ The scheme for the assistant message """

    id: int
    text: str
    role: Role
    created_at: datetime


__all__ = (
    'MessageSchema',
    'AssistantMessageSchema',
)
