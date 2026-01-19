import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.community import Community, Membership
    from app.models.social import Post, Comment, PostLike
    from app.models.listing import Listing
    # 🚨 THE FIX: Import MemberService for type checking
    from app.models.referral import MemberService

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    
    # --- PROFILE FIELDS ---
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
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # --- RELATIONSHIPS ---
    created_communities: List["Community"] = Relationship(back_populates="creator")
    memberships: List["Membership"] = Relationship(back_populates="user")
    posts: List["Post"] = Relationship(back_populates="author")
    
    # 🚨 THE FIX: The missing relationship
    services: List["MemberService"] = Relationship(back_populates="user")