import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

class LibraryPage(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    # Navigation
    slug: str = Field(index=True) # e.g. "getting-started"
    title: str
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="librarypage.id")
    
    # Content
    content: str # Markdown
    is_published: bool = Field(default=True)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    community: "Community" = Relationship()
    author: "User" = Relationship()
    
    # Self-Referential (Children)
    # Note: SQLModel requires a bit of specific typing for self-referential, 
    # but for MVP we will just query by parent_id manually or use simple joins.