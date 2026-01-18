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
    
    # --- 🆕 NEW PROFILE FIELDS (The Missing Piece) ---
    headline: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=500)
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    
    # --- SOCIAL LINKS ---
    website: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None
    
    # --- GAMIFICATION ---
    level: int = Field(default=1)
    xp: int = Field(default=0)
    reputation_score: int = Field(default=100)
    
    # --- RELATIONSHIPS ---
    created_communities: List["Community"] = Relationship(back_populates="creator")
    memberships: List["Membership"] = Relationship(back_populates="user")
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")
    liked_posts: List["PostLike"] = Relationship() 
    liked_comments: List["CommentLike"] = Relationship()