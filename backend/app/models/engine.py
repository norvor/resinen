import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.community import Community

# 1. THE LINK MODEL (Must be defined first)
class CommunityEngine(SQLModel, table=True):
    community_id: uuid.UUID = Field(foreign_key="community.id", primary_key=True)
    engine_id: uuid.UUID = Field(foreign_key="engine.id", primary_key=True)
    
    is_active: bool = True
    config_json: str = "{}" # JSON settings for this specific community
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 2. THE ENGINE DEFINITION
class Engine(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    key: str = Field(unique=True, index=True) # "academic", "social", "governance"
    name: str 
    description: str
    icon: str
    
    is_global: bool = False # If true, auto-installed for everyone
    
    # Relationship
    communities: List["Community"] = Relationship(
        back_populates="installed_engines",
        link_model=CommunityEngine
    )