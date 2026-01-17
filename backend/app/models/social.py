import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User
from app.models.community import Community

class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    # Content
    title: str
    body: str               # Markdown supported
    image_url: Optional[str] = None
    
    # Metadata
    slug: str               # For URL sharing (e.g. "my-first-post")
    view_count: int = 0
    
    # Governance Flags
    is_pinned: bool = False
    is_locked: bool = False # If thread is closed by mods
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    community: Community = Relationship(back_populates="posts")
    author: User = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    likes: List["PostLike"] = Relationship(back_populates="post")

class Comment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    post: Post = Relationship(back_populates="comments")
    author: User = Relationship(back_populates="comments")

class PostLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)
    
    post: Post = Relationship(back_populates="likes")