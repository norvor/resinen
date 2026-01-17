import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User

if TYPE_CHECKING:
    from app.models.community import Community, Chapter

# --- JOIN TABLE FOR LIKES ---
class PostLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    # --- CONTENT ---
    title: Optional[str] = None       # Useful for articles/questions
    content: str                      # Main body (Markdown supported)
    image_url: Optional[str] = None   # Featured image
    link_url: Optional[str] = None    # External link
    
    # --- MODERATION ---
    is_pinned: bool = Field(default=False) # Pin to top of feed
    is_locked: bool = Field(default=False) # No more comments allowed
    
    # --- METRICS ---
    like_count: int = Field(default=0)
    comment_count: int = Field(default=0) # Cache this to avoid expensive counts
    view_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    author: User = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    likes: List["PostLike"] = Relationship()

class Comment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    parent_id: Optional[uuid.UUID] = Field(default=None) # For nested replies (threading)
    
    content: str
    like_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    post: Post = Relationship(back_populates="comments")
    author: User = Relationship(back_populates="comments")