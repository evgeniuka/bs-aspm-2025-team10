from collections import defaultdict

from fastapi import WebSocket


class SessionRoomManager:
    def __init__(self) -> None:
        self._rooms: dict[int, set[WebSocket]] = defaultdict(set)

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
        stale: list[WebSocket] = []
        for websocket in list(self._rooms.get(session_id, set())):
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(session_id, websocket)


manager = SessionRoomManager()
