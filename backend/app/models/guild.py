import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.user import User

class BountyStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAID = "paid"

class GuildProject(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None
    tech_stack: Optional[str] = None
    
    likes: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    author: "User" = Relationship()

class GuildBounty(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    reward_text: str
    status: BountyStatus = Field(default=BountyStatus.OPEN)
    applicant_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    author: "User" = Relationship()