import uuid
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column

# 1. The "Link" Table (Many-to-Many with Payload)
# This tracks WHICH community has WHICH engine installed
class CommunityEngine(SQLModel, table=True):
    community_id: uuid.UUID = Field(foreign_key="community.id", primary_key=True)
    engine_id: uuid.UUID = Field(foreign_key="engine.id", primary_key=True)
    
    is_active: bool = Field(default=True)
    
    # Instance-specific config (e.g., "Who are the mentors for this community?")
    config: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))

# 2. The "Blueprint" Table
# This is the menu of available features (Academic, Referral, etc.)
class Engine(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # System Identifier (e.g., "academic_core", "referral_v1")
    key: str = Field(unique=True, index=True) 
    
    # Display Info
    name: str           # "The Academic Center"
    description: str    # "LMS and Knowledge Repository"
    icon: str           # "lucide-book-open"
    version: str        # "1.0.0"
    
    # Capabilities (Feature Flags for the UI)
    features: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    
    # Relationships
    communities: List["Community"] = Relationship(
        back_populates="installed_engines",
        link_model=CommunityEngine
    )