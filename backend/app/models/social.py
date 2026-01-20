import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# We import User because it is used in ForeignKeys directly
from app.models.user import User

if TYPE_CHECKING:
    # We only import these for Type Checking to avoid Circular Loops
    from app.models.community import Community, Chapter

# --- JOIN TABLE FOR POST LIKES ---
class PostLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- JOIN TABLE FOR COMMENT LIKES ---
class CommentLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    comment_id: uuid.UUID = Field(foreign_key="comment.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")

    # 🚨 THE FIX: Ensure this field exists for the relationship
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    # --- CONTENT ---
    content: str
    title: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    
    # --- MODERATION ---
    is_pinned: bool = Field(default=False)
    is_locked: bool = Field(default=False)
    
    # --- METRICS ---
    like_count: int = Field(default=0)
    comment_count: int = Field(default=0)
    view_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Relationships
    author: "User" = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"} 
    )
    likes: List["PostLike"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    # THE LINKS BACK
    community: "Community" = Relationship(back_populates="posts")
    
    # 🚨 THE FIX: The relationship partner to Chapter.posts
    chapter: Optional["Chapter"] = Relationship(back_populates="posts")

class Comment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    # --- HIERARCHY ---
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="comment.id")
    
    content: str
    like_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    post: "Post" = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="posts")
    
    # Self-Referential (Replies)
    children: List["Comment"] = Relationship(
        sa_relationship_kwargs={
            "cascade": "all, delete",
            "remote_side": "Comment.id"
        }
    )