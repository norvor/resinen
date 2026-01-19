import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import JSON, Column

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.social import Post
    from app.models.referral import MemberService

class Archetype(str, Enum):
    # Core
    SANCTUARY = "sanctuary" 
    BAZAAR = "bazaar"
    SENATE = "senate"
    ARENA = "arena"
    
    # Engines
    ACADEMY = "academy"
    CLUB = "club"
    LIBRARY = "library"
    STAGE = "stage"
    BUNKER = "bunker"
    GUILD = "guild"
    GARDEN = "garden"
    
    # Generic
    LOUNGE = "lounge"
    SPOTLIGHT = "spotlight"

class Membership(SQLModel, table=True):
    """Link between User and Community"""
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id", primary_key=True)
    
    role: str = Field(default="member") # owner, admin, mod, member
    status: str = Field(default="active") # active, pending, banned
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: "User" = Relationship(back_populates="memberships")
    community: "Community" = Relationship(back_populates="memberships")

class Chapter(SQLModel, table=True):
    """Sub-channels (like Discord Channels or Reddit Flairs)"""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    title: str
    description: Optional[str] = None
    sequence_order: int = 0
    
    community: "Community" = Relationship(back_populates="chapters")
    posts: List["Post"] = Relationship(back_populates="chapter")

class Community(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    slug: str = Field(unique=True, index=True)
    name: str
    description: Optional[str] = None
    
    banner_url: Optional[str] = None
    icon_url: Optional[str] = None
    primary_color: str = "#000000"
    
    is_private: bool = Field(default=False)
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    member_count: int = Field(default=1)
    
    # 🚨 THE FIX: Explicit SQLAlchemy Column Definitions for JSON Fields
    archetypes: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    installed_engines: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creator: "User" = Relationship(back_populates="created_communities")
    memberships: List["Membership"] = Relationship(back_populates="community")
    chapters: List["Chapter"] = Relationship(back_populates="community")
    posts: List["Post"] = Relationship(back_populates="community")
    services: List["MemberService"] = Relationship(back_populates="community")
    academic_resources: List["AcademicResource"] = Relationship(back_populates="community")