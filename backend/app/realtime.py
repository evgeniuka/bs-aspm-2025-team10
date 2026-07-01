import asyncio
from collections import defaultdict

from fastapi import WebSocket

MAX_CONNECTIONS_PER_SESSION = 25


class SessionRoomManager:
    def __init__(self) -> None:
        self._rooms: dict[int, set[WebSocket]] = defaultdict(set)

    def is_full(self, session_id: int) -> bool:
        return len(self._rooms.get(session_id, ())) >= MAX_CONNECTIONS_PER_SESSION

    async def connect(self, session_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms[session_id].add(websocket)

    def disconnect(self, session_id: int, websocket: WebSocket) -> None:
        room = self._rooms.get(session_id)
        if not room:
            return
        room.discard(websocket)
        if not room:
            self._rooms.pop(session_id, None)

    async def broadcast(self, session_id: int, payload: dict) -> None:
        sockets = list(self._rooms.get(session_id, set()))
        if not sockets:
            return
        results = await asyncio.gather(
            *(websocket.send_json(payload) for websocket in sockets),
            return_exceptions=True,
        )
        for websocket, result in zip(sockets, results):
            if isinstance(result, Exception):
                self.disconnect(session_id, websocket)


manager = SessionRoomManager()
