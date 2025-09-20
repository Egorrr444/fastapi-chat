from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models

app = FastAPI(
    title="Real-Time Chat API",
    description="Simple chat application with WebSockets",
    version="0.1.0"
)

# Настройка CORS (позже пригодится для фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в чат!",
        "status": "success",
        "endpoints": {
            "status": "/status",
            "users": "/users",
            "websocket": "/ws (WebSocket)",
            "documentation": "/docs"
        }
    }

@app.get("/status")
async def server_status():
    return {
        "status": "running",
        "server": "FastAPI",
        "version": "0.1.0"
    }

@app.get("/users")
async def list_users():
    # Заглушка - позже заменим реальными данными
    return {
        "users": [
            {"id": 1, "username": "user1"},
            {"id": 2, "username": "user2"}
        ],
        "total": 2
    }

# Заглушка для WebSocket 
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass


@app.on_event("startup")
async def startup_event():
    # Создаем таблицы в БД
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована")