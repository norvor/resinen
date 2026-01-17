import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.community import Community, Membership
    from app.models.social import Post, Comment, PostLike
    from app.models.referral import MemberService # If you use the referral module
    # from app.models.academic import AcademicResource # If you use the academic module

class User(SQLModel, table=True):
    # --- CORE AUTH ---
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    
    # --- STATUS & SECURITY ---
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_verified: bool = Field(default=False) # For email verification
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # --- RICH PROFILE ---
    avatar_url: Optional[str] = None      # Profile picture
    banner_url: Optional[str] = None      # Profile background
    headline: Optional[str] = None        # e.g. "Software Engineer @ Google"
    bio: Optional[str] = None             # Full markdown bio
    location: Optional[str] = None        # e.g. "San Francisco, CA"
    
    # --- SOCIAL LINKS ---
    website: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None

    # --- GAMIFICATION ---
    xp: int = Field(default=0)            # Experience points
    level: int = Field(default=1)         # Calculated level
    reputation_score: int = Field(default=0) 

    # --- RELATIONSHIPS ---
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")
    communities: List["Community"] = Relationship(back_populates="creator")
    memberships: List["Membership"] = Relationship(back_populates="user")
    
    # Optional Modules (Uncomment if you have these files)
    services: List["MemberService"] = Relationship(back_populates="user")