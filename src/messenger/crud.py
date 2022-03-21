from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload, aliased, selectinload

from core.db import get_session

from users.models import User

from avatars.models import Avatar, AvatarOnline
from avatars.services import update_avatars_online

from .types import Role, DialogSchema, ChatSchema, MessageSchema
from .models import Message, AssistantMessage

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def send_message(
    sender: User | Avatar,
    recipient: User | Avatar,
    text: str = None,
    photo_id: int = None,
    unread_mark: bool = True,
    session: 'AsyncSession' = None,
) -> Message:
    """
    Sends a message to an avatar or user

    :param sender: Sender must be avatar or user object
    :param recipient: Recipient must be avatar or user object
    :param text: Text of the message
    :param photo_id: Attachment is in the form of an image
    :param unread_mark: Is sent message unread
    :param session: Database session
    :return: Message model object
    """

    if type(sender) == type(recipient):
        raise AttributeError('The messenger does not support sending messages between the same types of senders')

    if not text and not photo_id:
        raise AttributeError('You cannot send an empty message, please attach either a text or a photo')

    if isinstance(sender, User):
        user = sender
        avatar = recipient
        role = Role.USER
    else:
        user = recipient
        avatar = sender
        role = Role.ASSISTANT

    message = Message(
        role=role,
        user_id=user.id,
        avatar_id=avatar.id,
        text=text,
        photo_id=photo_id,
        unread_mark=unread_mark,
    )

    session, is_new_session = get_session(session)

    session.add(message)
    await session.commit()

    if is_new_session:
        await session.close()

    return message


async def send_message_to_assistant(
    user: User,
    text: str,
    from_assistant: bool = False,
    session: 'AsyncSession' = None,
) -> AssistantMessage:
    """
    Sends a message to dating assistant

    :param user: User model object
    :param text: Text of the message
    :param from_assistant: Is this message from assistant or from user
    :param session: Database session
    :return: Message model object
    """

    message = AssistantMessage(
        role=Role.ASSISTANT if from_assistant else Role.USER,
        user_id=user.id,
        text=text,
    )

    session, is_new_session = get_session(session)

    session.add(message)
    await session.commit()

    if is_new_session:
        await session.close()

    return message


async def get_dialog_list(
    user: User,
    offset: int = None,
    limit: int = None,
    session: 'AsyncSession' = None,
) -> list[DialogSchema]:
    """
    Returns a list of user dialogs

    :param user: User model object
    :param offset: The number of dialogs that must be skipped to receive the following
    :param limit: The maximum number of dialogs to receive
    :param session: Database session
    :return: List of dialogs
    """

    session, is_new_session = get_session(session)

    await update_avatars_online(user=user, session=session)

    if offset is None:
        offset = 0

    AliasedMessage = aliased(Message)

    unread_subquery = select(func.count(AliasedMessage.id)).where(
        AliasedMessage.user_id == Message.user_id,
        AliasedMessage.avatar_id == Message.avatar_id,
        AliasedMessage.unread_mark == True,
    ).scalar_subquery()

    message_subquery = select(func.max(Message.id)).where(Message.user_id == user.id).group_by(Message.avatar_id)

    online_subquery = select(AvatarOnline.is_online).where(
        AvatarOnline.user_id == Message.user_id,
        AvatarOnline.avatar_id == Message.avatar_id,
    ).scalar_subquery()

    statement = select(Message, unread_subquery, online_subquery).where(
        Message.id.in_(message_subquery),
    ).order_by(Message.id.desc()).offset(offset).options(selectinload(Message.photo))

    if limit is not None and limit > 0:
        statement = statement.limit(limit)

    statement = statement.options(joinedload(Message.avatar).selectinload(Avatar.photo))

    query = await session.execute(statement)

    dialogs = []

    for top_message in query:
        is_avatar_online = top_message[2]
        unread_count = top_message[1]
        message = top_message[0]

        avatar_chat_schema = ChatSchema(
            id=message.avatar_id,
            name=message.avatar.name,
            is_online=is_avatar_online or False,
            is_avatar=True,
            photo=message.avatar.photo[0] if len(message.avatar.photo) > 0 else None,
        )

        top_message_schema = MessageSchema(
            id=message.id,
            text=message.text,
            photo=message.photo,
            unread_mark=message.unread_mark,
            created_at=message.created_at,
            from_user=avatar_chat_schema if message.role == Role.ASSISTANT else ChatSchema(
                id=user.id,
                name=user.login,
                is_online=True,
                is_avatar=False,
                photo=None,
            ),
        )

        dialogs.append(DialogSchema(
            unread_count=unread_count,
            chat=avatar_chat_schema,
            top_message=top_message_schema,
        ))

    if is_new_session:
        await session.close()

    return dialogs


async def get_dialog_messages(
    *participants: User | Avatar,
    offset: int = None,
    limit: int = None,
    session: 'AsyncSession' = None,
) -> list[Message]:
    """
    Returns a list of all messages between two interlocutors

    :param participants: Interlocutors (user and avatar)
    :param offset: The number of messages that must be skipped to receive the following
    :param limit: The maximum number of messages to receive
    :param session: Database session
    :return: List of the received messages
    """

    if len(participants) != 2:
        raise AttributeError('To receive messages, you need to transfer 2 participants of the dialogue')

    if offset is None:
        offset = 0

    user = participants[0] if isinstance(participants[0], User) else participants[1]
    avatar = participants[1] if user == participants[0] else participants[0]

    statement = select(Message).where(
        Message.user_id == user.id,
        Message.avatar_id == avatar.id,
    ).order_by(Message.created_at.desc()).offset(offset)

    if limit is not None and limit > 0:
        statement = statement.limit(limit)

    statement = statement.options(
        joinedload(Message.avatar).selectinload(Avatar.photo),
        joinedload(Message.user),
        joinedload(Message.photo),
    )

    session, is_new_session = get_session(session)

    query = await session.execute(statement)

    if is_new_session:
        await session.close()

    return query.scalars().all()


async def read_dialog_messages(user: 'User', avatar: 'Avatar', session: 'AsyncSession' = None) -> None:
    """
    Marks messages as read in the specified dialog

    :param user: User model object
    :param avatar: Avatar model object
    :param session: Database session
    :return:
    """

    statement = update(Message).where(
        Message.user_id == user.id,
        Message.avatar_id == avatar.id,
        Message.unread_mark == True,
    ).values(unread_mark=False)

    session, is_new_session = get_session(session)

    await session.execute(statement)
    await session.commit()

    if is_new_session:
        await session.close()


async def get_last_message_with_media_in_dialog(
    *participants: User | Avatar,
    session: 'AsyncSession' = None,
) -> Message | None:
    """
    Returns last exists message with media attachment in dialog between participants

    :param participants: Interlocutors (user and avatar)
    :param session: Database session
    :return: Message model object
    """

    if len(participants) != 2:
        raise AttributeError('To receive message, you need to transfer 2 participants of the dialogue')

    user = participants[0] if isinstance(participants[0], User) else participants[1]
    avatar = participants[1] if user == participants[0] else participants[0]

    statement = select(Message).where(
        Message.user_id == user.id,
        Message.avatar_id == avatar.id,
        Message.photo_id != None,
    ).order_by(Message.id.desc()).limit(1)

    session, is_new_session = get_session(session)

    query = await session.execute(statement)

    if is_new_session:
        await session.close()

    return query.scalar_one_or_none()


async def get_dialog_messages_count(
    *participants: User | Avatar,
    session: 'AsyncSession' = None,
) -> int:
    """
    Returns the total number of messages between 2 interlocutors

    :param participants: Interlocutors (user and avatar)
    :param session: Database session
    :return: Count of messages
    """

    if len(participants) != 2:
        raise AttributeError('To receive message, you need to transfer 2 participants of the dialogue')

    user = participants[0] if isinstance(participants[0], User) else participants[1]
    avatar = participants[1] if user == participants[0] else participants[0]

    statement = select(func.count(Message.id)).where(Message.user_id == user.id, Message.avatar_id == avatar.id)

    session, is_new_session = get_session(session)

    query = await session.execute(statement)

    if is_new_session:
        await session.close()

    return query.scalar_one_or_none()


async def get_messages_count_with_photo(
    *participants: User | Avatar,
    from_date: 'datetime',
    to_date: 'datetime',
    session: 'AsyncSession' = None,
) -> int:
    """
    Returns the number of messages with a photo in a given time interval

    :param participants: Interlocutors (user and avatar)
    :param from_date: Minimum date of the first message
    :param to_date: The maximum date of the last message
    :param session: Database session
    :return: Count of the messages with photo
    """

    if len(participants) != 2:
        raise AttributeError('To receive message, you need to transfer 2 participants of the dialogue')

    user = participants[0] if isinstance(participants[0], User) else participants[1]
    avatar = participants[1] if user == participants[0] else participants[0]

    statement = select(func.count(Message.id)).where(
        Message.user_id == user.id,
        Message.avatar_id == avatar.id,
        Message.created_at >= from_date,
        Message.created_at <= to_date,
        Message.photo_id != None
    )

    session, is_new_session = get_session(session)

    query = await session.execute(statement)

    if is_new_session:
        await session.close()

    return query.scalar_one_or_none()


async def get_dialog_messages_count_from_participant(
    *participants: User | Avatar,
    from_participant: User | Avatar,
    session: 'AsyncSession' = None,
) -> int:
    """
    Returns the total number of messages between 2 interlocutors

    :param participants: Interlocutors (user and avatar)
    :param from_participant: The sender to count the number of messages for
    :param session: Database session
    :return: Count of messages
    """

    if len(participants) != 2:
        raise AttributeError('To receive message, you need to transfer 2 participants of the dialogue')

    user = participants[0] if isinstance(participants[0], User) else participants[1]
    avatar = participants[1] if user == participants[0] else participants[0]

    statement = select(func.count(Message.id)).where(Message.user_id == user.id, Message.avatar_id == avatar.id)
    statement = statement.where(Message.role == (Role.ASSISTANT.value if from_participant.id == avatar.id else Role.USER.value))

    session, is_new_session = get_session(session)

    query = await session.execute(statement)

    if is_new_session:
        await session.close()

    return query.scalar_one_or_none()


async def get_assistant_messages_from_user(user: 'User', session: 'AsyncSession' = None) -> int:
    """
    Retrieve assistant messages count from specified user

    :param user: User model object
    :param session: Database session
    :return: Number of messages
    """

    session, is_new_session = get_session(session)
    statement = select(func.Count(AssistantMessage.id)).where(
        AssistantMessage.user_id == user.id,
        AssistantMessage.role == Role.USER,
    )

    query = await session.execute(statement)

    if is_new_session:
        await session.close()

    return query.scalar_one_or_none()


async def get_assistant_messages(
    user: 'User',
    offset: int = None,
    limit: int = None,
    session: 'AsyncSession' = None,
) -> list[AssistantMessage]:
    """
    Retrieve assistant messages list

    :param user: User model object
    :param offset: Offset for retrieving messages
    :param limit: Limit of messages
    :param session: Database session
    :return: Messages list between user and assistant
    """

    if offset is None:
        offset = 0

    statement = (select(AssistantMessage).where(AssistantMessage.user_id == user.id)
                 .order_by(AssistantMessage.created_at.desc()).offset(offset))

    if limit is not None and limit > 0:
        statement = statement.limit(limit)

    statement = statement.options(
        joinedload(AssistantMessage.user),
    )

    session, is_new_session = get_session(session)

    query = await session.execute(statement)

    if is_new_session:
        await session.close()

    return query.scalars().all()


__all__ = (
    'send_message',
    'get_dialog_list',
    'get_dialog_messages',
    'read_dialog_messages',
    'get_assistant_messages',
    'send_message_to_assistant',
    'get_dialog_messages_count',
    'get_messages_count_with_photo',
    'get_assistant_messages_from_user',
    'get_last_message_with_media_in_dialog',
    'get_dialog_messages_count_from_participant',
)
