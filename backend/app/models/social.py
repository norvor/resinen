import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.user import User

# Many-to-Many for Likes
class PostLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)

class Comment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="comment.id")
    
    content: str
    like_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    author: "User" = Relationship()

class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id", index=True)
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    content: str
    title: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    
    # Metrics
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    is_pinned: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    author: "User" = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates=None)