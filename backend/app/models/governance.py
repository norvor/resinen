import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column

# 1. THE CONSTITUTION (Global Laws - Set by You)
class GlobalLaw(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str              # e.g. "Zero Tolerance Policy"
    body: str               # e.g. "Any acts of violence..."
    severity: str           # "critical" (immediate ban), "standard"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

# 2. THE BYLAWS (Local Laws - Set by Community Admin)
class CommunityBylaw(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    title: str              # e.g. "No Political Debates"
    body: str
    enforcement_level: str  # "warn", "mute", "ban"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)