from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from . import models
from fastapi import Depends, HTTPException, status, Form
from . import auth, crud, schemas
from .database import get_db
from sqlalchemy.orm import Session
from datetime import timedelta
from .websocket import manager, get_user_from_websocket
import json
from fastapi import Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(
    title="Real-Time Chat API",
    description="Simple chat application with WebSockets",
    version="0.1.0"
)

current_dir = Path(__file__).resolve().parent  # Папка app
backend_dir = current_dir.parent              # Папка backend  
frontend_dir = backend_dir.parent / "frontend"

app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


# Настройка CORS (позже пригодится для фронтенда)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все origins
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)


@app.get("/")
async def read_root():
    return FileResponse(frontend_dir / "index.html")

@app.get("/style.css")
async def get_css():
    return FileResponse(frontend_dir / "style.css")

@app.get("/script.js")
async def get_js():
    return FileResponse(frontend_dir / "script.js")




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


@app.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Имя пользователя уже зарегистрировано")
    
    return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.UserResponse)
async def read_users_me(
    authorization: str = Header(None),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return current_user

 

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    
    # Аутентификация пользователя
    user = await get_user_from_websocket(websocket, token, db)
    if not user:
        return

    # Подключаем пользователя
    await manager.connect(websocket, user.id)
    
    try:
        while True:
            # Получаем сообщение от пользователя
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Сохраняем сообщение в БД
            db_message = crud.create_message(
                db=db,
                message=schemas.MessageCreate(text=message_data["text"]),
                user_id=user.id
            )
            
            # Формируем ответ с информацией о пользователе
            response = {
                "id": db_message.id,
                "text": db_message.text,
                "user_id": user.id,
                "username": user.username,
                "created_at": db_message.created_at.isoformat()
            }
            
            # Рассылаем сообщение всем подключенным пользователям
            await manager.broadcast(json.dumps(response))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
        # Уведомляем о выходе пользователя
        await manager.broadcast(json.dumps({
            "type": "user_left",
            "user_id": user.id,
            "username": user.username
        }))




@app.on_event("startup")
async def startup_event():
    # Создаем таблицы в БД
    Base.metadata.create_all(bind=engine)
    print("База данных инициализирована")