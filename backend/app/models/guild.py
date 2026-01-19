import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

class BountyStatus(str, Enum):
    OPEN = "open"
    CLAIMED = "claimed"
    CLOSED = "closed"

# --- 1. THE SHOWCASE (Project) ---
class GuildProject(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None
    
    # Tech Stack (Stored as comma-separated string for MVP, e.g. "React,Python,AWS")
    tech_stack: Optional[str] = None
    
    likes: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    community: "Community" = Relationship()
    author: "User" = Relationship()

# --- 2. THE JOB (Bounty) ---
class GuildBounty(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    reward_text: str # e.g. "$500" or "Equity" or "Good Vibes"
    
    status: BountyStatus = Field(default=BountyStatus.OPEN)
    applicant_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    community: "Community" = Relationship()
    author: "User" = Relationship()