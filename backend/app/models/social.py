import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User

# Forward references
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.community import Community, Chapter

class PostLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    content: str
    image_url: Optional[str] = None
    
    # We keep a count for fast sorting/display
    like_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    author: User = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    
    # Link to the Like table
    likes: List["PostLike"] = Relationship()

class Comment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    post: Post = Relationship(back_populates="comments")
    author: User = Relationship()