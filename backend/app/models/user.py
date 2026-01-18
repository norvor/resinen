import uuid
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.community import Community, Membership
    from app.models.social import Post, Comment, PostLike, CommentLike

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    
    # Gamification
    level: int = Field(default=1)
    xp: int = Field(default=0)
    reputation_score: int = Field(default=100)
    
    # Relationships
    # 1. Communities created by this user
    created_communities: List["Community"] = Relationship(back_populates="creator")
    
    # 2. Communities this user has joined
    memberships: List["Membership"] = Relationship(back_populates="user")
    
    # 3. Social Content
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")
    
    # 4. Likes (Forward references to join tables)
    liked_posts: List["PostLike"] = Relationship() 
    liked_comments: List["CommentLike"] = Relationship()

    # REMOVED: services: List["MemberService"] = ... (The ghost is gone)