import uuid
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import JSON, Column
from typing import List, Optional

class Engine(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key: str = Field(unique=True, index=True) # e.g. "social", "arena"
    name: str
    description: str
    icon: str # feather icon name
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityEngine(SQLModel, table=True):
    """
    Join table: Tracks which Community has installed which Engine.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    community_id: uuid.UUID = Field(foreign_key="community.id", index=True)
    engine_id: uuid.UUID = Field(foreign_key="engine.id")
    
    is_active: bool = Field(default=True)
    config: dict = Field(default_factory=dict, sa_column=Column(JSON)) # Specific settings for this install
    
    installed_at: datetime = Field(default_factory=datetime.utcnow)