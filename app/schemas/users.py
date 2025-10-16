from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    login: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=6, max_length=100)

    @validator('login')
    def login_alphanumeric(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Логин должен содержать только буквы, цифры и подчеркивания')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    login: Optional[str] = Field(None, min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserResponse(BaseModel):
    id: int
    email: str
    login: str
    created_at: datetime
    updated_at: datetime