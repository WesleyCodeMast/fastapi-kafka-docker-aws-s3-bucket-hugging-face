from core.db import get_session
from core.broadcaster import get_broadcast

from ai.types import Prompt
from ai.services import send_prompt, get_intent_classifier

from users.models import User
from users.schemas import UserAnswer
from users.dependencies import subscribed_user
from users.exceptions import UnsubscribedError

from avatars.services import set_avatar_online, get_random_farewell_message, get_random_photo_message

from media.services import get_media_by_id

from .crud import (
    send_message,
    get_dialog_messages,
    get_assistant_messages,
    send_message_to_assistant as _send_message_to_assistant,
    get_dialog_messages_count,
    get_messages_count_with_photo,
    get_assistant_messages_from_user,
    get_last_message_with_media_in_dialog,
    get_dialog_messages_count_from_participant,
)

from .types import Role, MessageSchema, ChatSchema, WSMessageSchema, WSTypingSchema
from .exceptions import OpenAIError

from functools import lru_cache
from datetime import datetime, timedelta, timezone
from typing import Union, TYPE_CHECKING

import asyncio

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from avatars.models import Avatar

    from .models import AssistantMessage


async def process_avatar_message(
    user: 'User',
    avatar: 'Avatar',
    text: str,
    session: 'AsyncSession' = None,
) -> None:
    """
    Process sent message to the avatar

    :param user: User model object
    :param avatar: Avatar model object
    :param text: Message text
    :param session: Database session
    :return:
    """

    broadcast = get_broadcast()

    await broadcast.publish(
        channel=f'user_{user.id}',
        message=WSMessageSchema(
            type='typing',
            content=WSTypingSchema(
                avatar_id=avatar.id,
            ),
        ).model_dump_json(),
    )

    session, is_new_session = get_session(session)

    tz = timezone(timedelta(hours=user.timezone))

    from_date = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0) \
        .astimezone(timezone.utc).replace(tzinfo=None)
    to_date = from_date + timedelta(days=1)
    limit_daily_image = False

    messages_with_photo_count = await get_messages_count_with_photo(
        user,
        avatar,
        from_date=from_date,
        to_date=to_date,
    )

    if messages_with_photo_count < 4:
        intent_classifier = get_intent_classifier()
        action = intent_classifier.validate_intent(text=text)

        if len(action) > 0 and action[0] == 'get_image' and len(avatar.message_photo) > 0:
            sent_message = await get_last_message_with_media_in_dialog(user, avatar)
            random_photo_message = await get_random_photo_message(session=session)

            if random_photo_message:
                await asyncio.sleep(2)

                sent_message = await send_message(
                    sender=avatar,
                    recipient=user,
                    text=random_photo_message,
                    session=session,
                )

                sent_message_schema = MessageSchema(
                    id=sent_message.id,
                    text=sent_message.text,
                    photo=None,
                    unread_mark=sent_message.unread_mark,
                    created_at=sent_message.created_at,
                    from_user=ChatSchema(
                        id=avatar.id,
                        name=avatar.name,
                        is_online=True,
                        is_avatar=True,
                        photo=avatar.photo[0] if len(avatar.photo) > 0 else None,
                    ),
                )

                await broadcast.publish(
                    channel=f'user_{user.id}',
                    message=WSMessageSchema(
                        type='message',
                        content=sent_message_schema,
                    ).model_dump_json(),
                )

            await asyncio.sleep(3)

            if sent_message is not None:
                sent_photo_index = None

                for i, photo in enumerate(avatar.message_photo):
                    if photo.id == sent_message.photo_id:
                        sent_photo_index = i
                        break

                if sent_photo_index is not None:
                    if sent_photo_index + 1 >= len(avatar.message_photo):
                        sent_photo_index = 0
                    else:
                        sent_photo_index += 1
                else:
                    sent_photo_index = 0

                photo_to_send = avatar.message_photo[sent_photo_index]
            else:
                photo_to_send = avatar.message_photo[0]

            message = await send_message(sender=avatar, recipient=user, photo_id=photo_to_send.id, session=session)
        else:
            system_prompt = _get_system_prompt_by_avatar(avatar=avatar)
            previous_messages = (await get_dialog_messages(user, avatar, limit=5, session=session))[::-1]

            messages = [
                Prompt(
                    role='user' if x.role == Role.USER else 'assistant',
                    content=x.text,
                ) for x in previous_messages if x.text
            ]

            prompts = [system_prompt] + messages

            openai_reply = await send_prompt(messages=prompts)

            if not openai_reply:
                raise OpenAIError()

            reply_text = openai_reply.choices[0].message.content

            message = await send_message(sender=avatar, recipient=user, text=reply_text, session=session)
    else:
        farewell_message = await get_random_farewell_message(avatar=avatar, session=session)
        message = await send_message(sender=avatar, recipient=user, text=farewell_message, session=session)

        intent_classifier = get_intent_classifier()
        action = intent_classifier.validate_intent(text=text)

        if len(action) > 0 and action[0] == 'get_image':
            limit_daily_image = True

    await set_avatar_online(user=user, avatar=avatar, session=session)

    if is_new_session:
        await session.close()

    if message.photo_id is not None:
        photo = await get_media_by_id(media_id=message.photo_id, session=session)
    else:
        photo = None

    schema = MessageSchema(
        id=message.id,
        text=message.text,
        photo=photo,
        unread_mark=message.unread_mark,
        created_at=message.created_at,
        limit_daily_image=limit_daily_image,
        from_user=ChatSchema(
            id=avatar.id,
            name=avatar.name,
            is_online=True,
            is_avatar=True,
            photo=avatar.photo[0] if len(avatar.photo) > 0 else None,
        ),
    )

    await broadcast.publish(
        channel=f'user_{user.id}',
        message=WSMessageSchema(
            type='message',
            content=schema,
        ).model_dump_json(),
    )


async def send_message_to_avatar(
    user: 'User',
    avatar: 'Avatar',
    text: str,
    session: 'AsyncSession' = None,
) -> MessageSchema:
    """
    Sends a message to the avatar on behalf of the user

    :param user: User model object
    :param avatar: Avatar model object
    :param text: Message text
    :param session: Database session
    :return: Message model object (avatar answer)
    """

    session, is_new_session = get_session(session)

    try:
        await subscribed_user(user=user, session=session)

        is_user_subscribed = True
    except UnsubscribedError:
        is_user_subscribed = False

    if not is_user_subscribed:
        messages_count = await get_dialog_messages_count_from_participant(
            user,
            avatar,
            from_participant=user,
            session=session,
        )

        if messages_count >= 15:
            raise UnsubscribedError()

    message = await send_message(sender=user, recipient=avatar, text=text, unread_mark=False, session=session)

    if is_new_session:
        await session.close()

    asyncio.create_task(process_avatar_message(user=user, avatar=avatar, text=text))

    return MessageSchema(
        id=message.id,
        text=message.text,
        photo=None,
        unread_mark=False,
        created_at=message.created_at,
        from_user=ChatSchema(
            id=user.id,
            name=user.login,
            is_online=True,
            is_avatar=False,
            photo=None,
        ),
    )


async def send_message_to_assistant(
    user: 'User',
    text: str,
    session: 'AsyncSession' = None,
) -> 'AssistantMessage':
    """
    Send new message to the dating assistant

    :param user: User model object
    :param text: Message text
    :param session: Database session
    :return: Message model object
    """

    session, is_new_session = get_session(session=session)

    try:
        await subscribed_user(user=user, session=session)

        is_user_subscribed = True
    except UnsubscribedError:
        is_user_subscribed = False

    if not is_user_subscribed:
        messages_count = await get_assistant_messages_from_user(user=user, session=session)

        if messages_count >= 10:
            raise UnsubscribedError()

    await _send_message_to_assistant(user=user, text=text, session=session)

    system_prompt = _get_assistant_system_prompts()
    previous_messages = (await get_assistant_messages(user=user, limit=5, session=session))[::-1]

    messages = [
        Prompt(
            role='user' if x.role == Role.USER else 'assistant',
            content=x.text,
        ) for x in previous_messages if x.text
    ]

    prompts = [system_prompt] + messages

    openai_reply = await send_prompt(messages=prompts)

    if not openai_reply:
        raise OpenAIError()

    reply_text = openai_reply.choices[0].message.content

    message = await _send_message_to_assistant(user=user, text=reply_text, from_assistant=True, session=session)

    return message


async def get_messages(
    *participants: Union['User', 'Avatar'],
    offset: int = None,
    limit: int = None,
    session: 'AsyncSession' = None,
) -> list[MessageSchema]:
    """
    Returns a list of all messages between two interlocutors

    :param participants: Interlocutors (user and avatar)
    :param offset: The number of messages that must be skipped to receive the following
    :param limit: The maximum number of messages to receive
    :param session: Database session
    :return: List of the received messages
    """

    session, is_new_session = get_session(session=session)

    messages_count = await get_dialog_messages_count(*participants, session=session)

    avatar: 'Avatar' = participants[1] if isinstance(participants[0], User) else participants[0]
    user: 'User' = participants[0] if isinstance(participants[0], User) else participants[1]

    if messages_count == 0 and len(avatar.hello_messages) > 0:
        for hello_message in avatar.hello_messages:
            await send_message(sender=avatar, recipient=user, text=hello_message.text, session=session)

    messages = await get_dialog_messages(*participants, offset=offset, limit=limit, session=session)

    if is_new_session:
        await session.close()

    return [
        MessageSchema(
            id=x.id,
            text=x.text,
            photo=x.photo,
            unread_mark=x.unread_mark,
            created_at=x.created_at,
            from_user=ChatSchema(
                **(
                    {'id': x.user_id, 'name': x.user.login, 'is_online': True, 'is_avatar': False, 'photo': None}
                    if x.role == Role.USER else
                    {
                        'id': x.avatar_id,
                        'name': x.avatar.name,
                        'is_online': False,
                        'is_avatar': True,
                        'photo': x.avatar.photo[0] if len(x.avatar.photo) > 0 else None,
                    }
                )
            ),
        ) for x in messages
    ]


def _get_system_prompt_by_avatar(avatar: 'Avatar') -> Prompt:
    """
    Generates a system prompt for the avatar

    :param avatar: Avatar model object
    :return: System prompt instance
    """

    return Prompt(
        role='system',
        content='Ты добавлен внутрь приложения. Твоя задача общаться от имени разных персонажей и вести '
                'диалог с пользователем. Я задам тебе возраст, имя, твое описание личности, пол и готовность к '
                'общению на интимные темы. Ты будешь отвечать на сообщения пользователя:\n'
                f'Возраст - {avatar.age}\n'
                f'Имя - {avatar.name}\n'
                f'Твое описание - {avatar.biography}\n'
                f'Общение на антимные темы: {"нет" if avatar.spicy_conversations == UserAnswer.NO else "да"}',
    )


@lru_cache
def _get_assistant_system_prompts() -> Prompt:
    """
    Retrieve system prompts for dating assistant

    :return: System prompt for dating assistant
    """

    return Prompt(
        role='system',
        content='You should act as a dating assistant. The user will ask you a question or ask for help '
                'writing a message, and you should help them with the response.',
    )


__all__ = (
    'send_message_to_assistant',
    'send_message_to_avatar',
    'get_messages',
)
