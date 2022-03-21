from sqlalchemy import ForeignKey, Text, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import BaseModel, TimestampMixin

from users.models import User
from avatars.models import Avatar
from media.models import Media

from .types import Role

from typing import TYPE_CHECKING


class Message(BaseModel, TimestampMixin):
    """
    The essence of the message in the context of the user's
    communication with the chat assistant
    """

    __tablename__ = 'messages'

    if TYPE_CHECKING:
        role: Role
        user_id: int
        user: User
        avatar_id: int | None
        avatar: Avatar | None
        text: str
        unread_mark: bool
        photo_id: int | None
        photo: Media | None
    else:
        role: Mapped[Role] = mapped_column(SqlEnum(Role))
        # The role of the sender of the message

        user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
        # The ID of the user who sent or received the message

        user: Mapped[User] = relationship(User)
        # The user who sent or received the message

        avatar_id: Mapped[int] = mapped_column(ForeignKey('avatars.id'))
        # The ID of the avatar who sent or received the message

        avatar: Mapped[Avatar] = relationship(Avatar)
        # The user who sent or received the message

        text: Mapped[str] = mapped_column(Text, default=None, nullable=True)
        # The text sent in this message

        unread_mark: Mapped[bool] = mapped_column(default=True)
        # Is this message unread

        photo_id: Mapped[int] = mapped_column(ForeignKey('media.id'), default=None, nullable=True)
        # Identifier of the image attached to this message

        photo: Mapped[Media] = relationship(Media)
        # Image attached to this message


class AssistantMessage(BaseModel, TimestampMixin):
    """ A message model describing the communication between the user and the dating assistant """

    __tablename__ = 'assistant_messages'

    if TYPE_CHECKING:
        role: Role
        user_id: int
        user: User
        text: str
    else:
        role: Mapped[Role] = mapped_column(SqlEnum(Role))
        # The role of the sender of the message

        user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
        # The ID of the user who sent or received the message

        user: Mapped[User] = relationship(User)
        # The user who sent or received the message

        text: Mapped[str] = mapped_column(Text, default=None, nullable=True)
        # The text sent in this message


__all__ = (
    'Message',
    'AssistantMessage',
)
