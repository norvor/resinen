import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

class StageVideo(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    # Content
    title: Optional[str] = None # Caption
    video_url: str
    thumbnail_url: str
    
    # Tech Specs
    duration_sec: int = Field(default=0)
    aspect_ratio: str = Field(default="9:16") # usually vertical
    
    # Metrics
    view_count: int = Field(default=0)
    like_count: int = Field(default=0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    community: "Community" = Relationship()
    author: "User" = Relationship()