import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community, Chapter

# --- 1. LIKES ---
class CommentLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    comment_id: uuid.UUID = Field(foreign_key="comment.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    comment: "Comment" = Relationship(back_populates="likes")

class PostLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    post: "Post" = Relationship(back_populates="likes")
    user: "User" = Relationship(back_populates="post_likes")

# --- 2. COMMENTS ---
class Comment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    post_id: uuid.UUID = Field(foreign_key="post.id")
    
    # 🚨 FIX: Added this field 🚨
    like_count: int = 0

    post: "Post" = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="comments")
    likes: List["CommentLike"] = Relationship(
        back_populates="comment",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

# --- 3. POSTS ---
class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    
    title: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    is_pinned: bool = False
    
    like_count: int = 0
    comment_count: int = 0
    view_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    author: "User" = Relationship(back_populates="posts")
    chapter: Optional["Chapter"] = Relationship(back_populates="posts")
    community: "Community" = Relationship(back_populates="posts")
    
    comments: List["Comment"] = Relationship(
        back_populates="post", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    likes: List["PostLike"] = Relationship(
        back_populates="post", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )