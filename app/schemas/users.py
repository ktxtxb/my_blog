from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    login: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=6, max_length=72)
    is_admin: bool = False  # создание админа

    @validator('login')
    def login_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Логин должен содержать только буквы, цифры и подчеркивания')
        if len(v) > 20:
            raise ValueError('Логин не может быть длиннее 20 символов')
        return v

    @validator('password')
    def password_length(cls, v):
        if len(v) > 72:
            raise ValueError('Пароль не может быть длиннее 72 символов')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    login: Optional[str] = Field(None, min_length=3, max_length=20, pattern="^[a-zA-Z0-9_]+$")
    password: Optional[str] = Field(None, min_length=6, max_length=72)
    is_admin: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    email: str
    login: str
    is_admin: bool  #
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    login: str
    is_admin: bool