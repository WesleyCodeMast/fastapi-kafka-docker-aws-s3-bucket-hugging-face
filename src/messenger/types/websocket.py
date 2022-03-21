from core.schemas import BaseSchema

from .message import MessageSchema


class WSTypingSchema(BaseSchema):
    """ WebSocket typing object """

    avatar_id: int


class WSMessageSchema(BaseSchema):
    """ WebSocket message object """

    type: str
    content: MessageSchema | WSTypingSchema | None = None


__all__ = (
    'WSTypingSchema',
    'WSMessageSchema',
)
