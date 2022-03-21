from enum import Enum


class Role(str, Enum):
    """ The role of the sender of the message """

    USER = 'user'
    ASSISTANT = 'assistant'


__all__ = (
    'Role',
)
