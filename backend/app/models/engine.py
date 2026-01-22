import uuid
from typing import Optional, List, Dict
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON, Column

# 1. The Join Table (User <-> Engine)
class UserEngine(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    engine_id: uuid.UUID = Field(foreign_key="engine.id", primary_key=True)
    
    # 🚨 THESE FIELDS WERE MISSING OR NOT DEFINED CORRECTLY
    is_active: bool = True
    is_pinned: bool = Field(default=False) 
    config: Dict = Field(default={}, sa_column=Column(JSON))

# 2. The Engine Definition
class Engine(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key: str = Field(index=True, unique=True) # e.g., 'journal', 'vault'
    name: str
    description: str
    icon: str
    is_system: bool = False 
    
    # Relationships
    users: List["User"] = Relationship(back_populates="engines", link_model=UserEngine)