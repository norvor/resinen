import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User

# 1. IMPORT THE ENGINE MODELS (So we can use the Class, not a string)
from app.models.engine import Engine, CommunityEngine

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
    rules: Optional[str] = None
    
    # --- BRANDING ---
    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    primary_color: Optional[str] = None
    
    # --- SETTINGS ---
    is_private: bool = Field(default=False)
    allow_alias: bool = Field(default=False)
    
    # --- METADATA ---
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    member_count: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # --- RELATIONSHIPS ---
    creator: User = Relationship(back_populates="communities")
    chapters: List["Chapter"] = Relationship(back_populates="community")
    memberships: List["Membership"] = Relationship(back_populates="community")
    services: List["MemberService"] = Relationship(back_populates="community")
    academic_resources: List["AcademicResource"] = Relationship(back_populates="community")
    posts: List["Post"] = Relationship(back_populates="community")
    
    # --- ENGINE SYSTEM (Fixed) ---
    # Now we pass the ACTUAL CLASS 'CommunityEngine', which fixes the inspection error.
    installed_engines: List[Engine] = Relationship(
        back_populates="communities",
        link_model=CommunityEngine 
    )

class Chapter(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    name: str 
    location: str = Field(default="Global") 
    description: Optional[str] = None
    banner_url: Optional[str] = None
    
    is_private: bool = Field(default=False)
    is_locked: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    community: Community = Relationship(back_populates="chapters")
    memberships: List["Membership"] = Relationship(back_populates="chapter")
    posts: List["Post"] = Relationship(back_populates="chapter")

class Membership(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    community_id: uuid.UUID = Field(foreign_key="community.id")
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    
    role: str = Field(default="member")
    status: str = Field(default="active")
    
    is_muted: bool = Field(default=False)
    muted_until: Optional[datetime] = None
    
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="memberships")
    community: Community = Relationship(back_populates="memberships")
    chapter: Optional[Chapter] = Relationship(back_populates="memberships")