import uuid
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
# 1. Import the link table
from app.models.links import UserEngine

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    avatar_url: Optional[str] = None
    
    # 2. Use the ACTUAL CLASS (UserEngine), not a string
    engines: List["Engine"] = Relationship(back_populates="users", link_model=UserEngine)