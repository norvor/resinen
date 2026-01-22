import uuid
from typing import List
from sqlmodel import SQLModel, Field, Relationship
# 1. Import the link table
from app.models.links import UserEngine

# (UserEngine class is REMOVED from here because it's in links.py now)

class Engine(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key: str = Field(index=True, unique=True)
    name: str
    description: str
    icon: str
    is_system: bool = False 
    
    # 2. Use the ACTUAL CLASS (UserEngine)
    users: List["User"] = Relationship(back_populates="engines", link_model=UserEngine)