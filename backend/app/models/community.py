import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User

# Avoid circular imports for Social
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.social import Post

class Community(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creator: User = Relationship(back_populates="communities")
    chapters: List["Chapter"] = Relationship(back_populates="community")

class Chapter(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    # --- THIS WAS LIKELY MISSING OR MISNAMED ---
    name: str 
    # -------------------------------------------
    
    location: str = Field(default="Global") 
    description: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    community: Community = Relationship(back_populates="chapters")
    # If you have posts/social logic, link them here
    # posts: List["Post"] = Relationship(back_populates="chapter")