import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.community import Community, Membership
    from app.models.social import Post, Comment, PostLike
    from app.models.listing import Listing

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    
    # Profile
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    
    # Social Links
    website: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None
    
    # System Flags
    is_active: bool = True
    is_superuser: bool = False
    
    # Gamification
    xp: int = Field(default=0)
    level: int = Field(default=1)
    reputation_score: int = Field(default=100)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    created_communities: List["Community"] = Relationship(back_populates="creator")
    memberships: List["Membership"] = Relationship(back_populates="user")
    posts: List["Post"] = Relationship(back_populates="author")