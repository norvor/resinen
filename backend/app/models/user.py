import uuid
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# 🚨 Import the Join Table from engine.py (Avoid circular imports by using quotes in type hints)
# We don't need to import UserEngine directly here if we use string forward references, 
# but we do need to make sure the file is loaded.

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    avatar_url: Optional[str] = None
    
    # 🚨 ADD THIS RELATIONSHIP
    # This matches the 'users' relationship in Engine
    engines: List["Engine"] = Relationship(back_populates="users", link_model="UserEngine")