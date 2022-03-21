from core.schemas import BaseSchema

from .chat import ChatSchema
from .message import MessageSchema


class DialogSchema(BaseSchema):
    """ The basic scheme of the dialogue """

    unread_count: int
    chat: ChatSchema
    top_message: MessageSchema


__all__ = (
    'DialogSchema',
)
