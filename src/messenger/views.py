from fastapi import APIRouter, Query, Depends, Body, WebSocket, WebSocketDisconnect

from core.schemas import StatusSchema
from core.broadcaster import get_broadcast

from users.dependencies import current_user, ws_current_user

from avatars.dependencies import validate_avatar_id

from .types import DialogSchema, MessageSchema, AssistantMessageSchema
from .crud import get_dialog_list, read_dialog_messages, get_assistant_messages
from .services import send_message_to_avatar, get_messages, send_message_to_assistant

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from users.models import User

    from avatars.models import Avatar

    from .models import AssistantMessage


router = APIRouter()


@router.get(path='/dialogs', response_model=list[DialogSchema])
async def dialogs_list_view(
    user: 'User' = Depends(current_user),
    offset: int = Query(ge=0, default=0),
    limit: int = Query(ge=1, le=100, default=20),
) -> list[DialogSchema]:
    """ An API method for getting a list of dialogs """

    return await get_dialog_list(
        user=user,
        offset=offset,
        limit=limit,
    )


@router.websocket(path='/ws')
async def messenger_websocket(
    websocket: WebSocket,
    user: 'User' = Depends(ws_current_user),
) -> None:
    """ A websocket for exchanging information about user actions with dialogs """

    await websocket.accept()

    broadcast = get_broadcast()

    try:
        async with broadcast.subscribe(channel=f'user_{user.id}') as subscriber:
            async for event in subscriber:
                await websocket.send_text(event.message)
    except WebSocketDisconnect:
        return


@router.post('/assistant/send', response_model=AssistantMessageSchema)
async def send_assistant_message_view(
    text: str = Body(embed=True),
    user: 'User' = Depends(current_user),
) -> 'AssistantMessage':
    """ An API method for sending a new message to the dating assistant """

    return await send_message_to_assistant(
        user=user,
        text=text,
    )


@router.get('/assistant', response_model=list[AssistantMessageSchema])
async def assistant_messages_list_view(
    user: 'User' = Depends(current_user),
    offset: int = Query(ge=0, default=0),
    limit: int = Query(ge=1, le=100, default=20),
) -> list['AssistantMessage']:
    """ An API method for getting a list of messages for specified dialog """

    return await get_assistant_messages(user=user, offset=offset, limit=limit)


@router.get('/{recipient_id}', response_model=list[MessageSchema])
async def messages_list_view(
    avatar: 'Avatar' = Depends(validate_avatar_id),
    user: 'User' = Depends(current_user),
    offset: int = Query(ge=0, default=0),
    limit: int = Query(ge=1, le=100, default=20),
) -> list[MessageSchema]:
    """ An API method for getting a list of messages for specified dialog """

    return await get_messages(avatar, user, offset=offset, limit=limit)


@router.post(path='/{recipient_id}/send', response_model=MessageSchema)
async def send_message_view(
    text: str = Body(embed=True),
    avatar: 'Avatar' = Depends(validate_avatar_id),
    user: 'User' = Depends(current_user),
) -> MessageSchema:
    """ An API method for sending a new message """

    return await send_message_to_avatar(
        user=user,
        avatar=avatar,
        text=text,
    )


@router.post('/{recipient_id}/read', response_model=StatusSchema)
async def mark_read_view(
    avatar: 'Avatar' = Depends(validate_avatar_id),
    user: 'User' = Depends(current_user),
) -> dict:
    """ An API method for updating the status of reading messages """

    await read_dialog_messages(user=user, avatar=avatar)

    return {'status': True}


__all__ = (
    'router',
)
