import uuid
from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class LibraryPage(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    slug: str
    title: str
    content: str
    is_published: bool = True
    
    # Recursion for Tree Structure
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="librarypage.id")
    children: List["LibraryPage"] = Relationship(
        sa_relationship_kwargs={
            "cascade": "all, delete",
            "remote_side": "LibraryPage.id"
        }
    )
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)