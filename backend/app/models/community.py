import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User

if TYPE_CHECKING:
    from app.models.social import Post
    from app.models.referral import MemberService
    from app.models.academic import AcademicResource

class Community(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # --- INFO ---
    name: str
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    rules: Optional[str] = None           # Community guidelines
    
    # --- BRANDING ---
    icon_url: Optional[str] = None        # Small logo
    banner_url: Optional[str] = None      # Large header image
    primary_color: Optional[str] = None   # For theming
    
    # --- SETTINGS ---
    is_private: bool = Field(default=False)
    allow_alias: bool = Field(default=False) # Can users post anonymously?
    
    # --- METADATA ---
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    member_count: int = Field(default=1)  # Cache for performance
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # --- RELATIONSHIPS ---
    creator: User = Relationship(back_populates="communities")
    chapters: List["Chapter"] = Relationship(back_populates="community")
    memberships: List["Membership"] = Relationship(back_populates="community")
    
    # Modules
    services: List["MemberService"] = Relationship(back_populates="community")
    academic_resources: List["AcademicResource"] = Relationship(back_populates="community")

class Chapter(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    name: str 
    location: str = Field(default="Global") 
    description: Optional[str] = None
    banner_url: Optional[str] = None
    
    # --- SETTINGS ---
    is_private: bool = Field(default=False)
    is_locked: bool = Field(default=False) # Only admins can post
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    community: Community = Relationship(back_populates="chapters")
    memberships: List["Membership"] = Relationship(back_populates="chapter")

class Membership(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    community_id: uuid.UUID = Field(foreign_key="community.id")
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    
    # --- ROLES & STATUS ---
    role: str = Field(default="member")   # member, moderator, admin
    status: str = Field(default="active") # active, pending, banned
    
    # --- MODERATION ---
    is_muted: bool = Field(default=False)
    muted_until: Optional[datetime] = None
    
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="memberships")
    community: Community = Relationship(back_populates="memberships")
    chapter: Optional[Chapter] = Relationship(back_populates="memberships")