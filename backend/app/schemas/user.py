from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: Optional[UUID] = None
    level: int = 1
    xp: int = 0
    reputation_score: int = 100

    class Config:
        from_attributes = True # ✅ FIX: Changed from 'orm_mode'

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str