from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
        username: str
        password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime


    class Config:
         orm_mode = True



class MessageBase(BaseModel):
    text: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    user_id: int
    created_at: datetime
    user: UserResponse
    
    class Config:
        orm_mode = True

# Схема для токена
class Token(BaseModel):
    access_token: str
    token_type: str

#Для хранения данных в токене 
class TokenData(BaseModel):
    username: Optional[str] = None