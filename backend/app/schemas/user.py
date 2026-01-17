from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    full_name: str

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None

# Properties to return via API (Never return the password!)
class UserRead(UserBase):
    id: UUID
    
    class Config:
        orm_mode = True