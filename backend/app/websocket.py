from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from . import crud, auth
from .database import get_db

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)

    async def broadcast(self, message: str):
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                await connection.send_text(message)

# Создаем экземпляр менеджера
manager = ConnectionManager()

# Функция для получения пользователя из WebSocket
async def get_user_from_websocket(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    try:
        user = await auth.get_current_user(token=token, db=db)
        return user
    except Exception:
        await websocket.close(code=1008)
        return None