from sqlalchemy.orm import Session
from . import models, schemas


def create_user(db: Session, user: schemas.UserCreate):
    # Сохраняем пароль как есть
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=user.password  
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_password(plain_password, hashed_password):
    
    return plain_password == hashed_password


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_messages(db: Session, user_id: int):
    return db.query(models.Message).filter(models.Message.user_id == user_id).all()

def create_message(db: Session, message: schemas.MessageCreate, user_id: int):
    db_message = models.Message(
        text=message.text,
        user_id=user_id
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_message(db: Session, message_id: int):
    return db.query(models.Message).filter(models.Message.id == message_id).first()
