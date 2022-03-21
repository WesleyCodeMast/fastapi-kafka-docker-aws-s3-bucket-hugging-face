from ..types import WSMessageSchema

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import WebSocket


class ConnectionManager:
    _active_connections: dict[int, list['WebSocket']]

    def __init__(self) -> None:
        """ WebSocket connections manager """

        self._active_connections = {}

    async def broadcast(self, user_id: int, message: WSMessageSchema) -> None:
        """
        Broadcast message to specified user

        :param user_id: User identifier
        :param message: Message object
        :return:
        """

        if user_id not in self._active_connections:
            return

        message_json = message.model_dump_json()

        for websocket in self._active_connections[user_id]:
            await websocket.send_text(message_json)

    async def connect(self, user_id: int, websocket: 'WebSocket') -> None:
        """
        Accept websocket connection for specified user

        :param user_id: User identifier
        :param websocket: WebSocket connection
        :return:
        """

        await websocket.accept()

        if user_id not in self._active_connections:
            self._active_connections[user_id] = []

        self._active_connections[user_id].append(websocket)

    def disconnect(self, user_id: int, websocket: 'WebSocket') -> None:
        """
        Remove websocket connection for specified user

        :param user_id: User identifier
        :param websocket: WebSocket connection
        :return:
        """

        selected_identifier = None
        is_connection_found = user_id in self._active_connections and websocket in self._active_connections[user_id]

        if not is_connection_found:
            for connection_user_id in self._active_connections.keys():
                if websocket in self._active_connections[connection_user_id]:
                    selected_identifier = connection_user_id
                    break
        else:
            selected_identifier = user_id

        if not selected_identifier or not self._active_connections[selected_identifier]:
            return

        self._active_connections[selected_identifier].remove(websocket)

        if len(self._active_connections[selected_identifier]) == 0:
            del self._active_connections[selected_identifier]


__all__ = (
    'ConnectionManager',
)
