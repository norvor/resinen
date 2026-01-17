import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

class PlatformRule(SQLModel, table=True):
    """
    The Constitution. These are the 'Hard Rules' set by Resinen.
    No community can disable these.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str              # e.g., "Zero Tolerance for Violence"
    description: str        # "Any threat of physical harm..."
    severity: str           # "critical" (immediate ban), "warning"
    
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityBylaw(SQLModel, table=True):
    """
    The Local Laws. These are specific to a 'Social Media' (Community).
    e.g., 'Sikh History Group' might ban 'Political Debates'.
    """
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    rule_key: str           # "allow_politics", "allow_nsfw"
    rule_value: str         # "false", "true", "restricted"
    description: str        
    
    created_at: datetime = Field(default_factory=datetime.utcnow)