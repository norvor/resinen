import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

# Received on Creation (Sign Up)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

# Returned to Frontend (Safe Data)
class UserRead(UserBase):
    id: uuid.UUID
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True