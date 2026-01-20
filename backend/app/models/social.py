import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

# We import User because it is used in ForeignKeys directly
from app.models.user import User

if TYPE_CHECKING:
    # We only import these for Type Checking to avoid Circular Loops
    from app.models.community import Community, Chapter

# --- JOIN TABLE FOR COMMENT LIKES ---
class CommentLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    comment_id: uuid.UUID = Field(foreign_key="comment.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PostLike(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 🚨 THE FIX: Add this line so Post can find it
    post: "Post" = Relationship(back_populates="likes")
    
    # Optional: Link to user
    user: "User" = Relationship(back_populates="likes") # Ensure User model has 'likes' list if you use this

# --- 2. COMMENT (Check this too) ---
class Comment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user_id: uuid.UUID = Field(foreign_key="user.id")
    post_id: uuid.UUID = Field(foreign_key="post.id")

    # 🚨 Ensure this exists too
    post: "Post" = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="comments")

# --- 3. POST (Your existing code with Cascade) ---
class Post(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    is_pinned: bool = False
    
    like_count: int = 0
    comment_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    author: "User" = Relationship(back_populates="posts")
    
    # The Cascades we added earlier
    comments: List["Comment"] = Relationship(
        back_populates="post", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    
    likes: List["PostLike"] = Relationship(
        back_populates="post", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )