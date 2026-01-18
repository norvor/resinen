import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON 

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.social import Post

# --- 1. THE 11 SOVEREIGN ARCHETYPES ---
class Archetype(str, Enum):
    ARENA = "arena"       # Sports / Competition
    STAGE = "stage"       # K-Pop / Art / Visual
    SANCTUARY = "sanctuary" # Faith / Wellness
    LIBRARY = "library"   # Anime / Lore / History
    GUILD = "guild"       # Coding / Makers
    BAZAAR = "bazaar"     # Commerce / Trading
    SENATE = "senate"     # Politics / Activism
    ACADEMY = "academy"   # Education / Bootcamp
    CLUB = "club"         # Nightlife / Dating
    BUNKER = "bunker"     # Anon / Secrets
    LOUNGE = "lounge"     # Social / Meetups
    DEFAULT = "default"   # Standard Town Square

# --- MEMBERSHIPS ---
class Membership(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id", primary_key=True)
    
    role: str = Field(default="member") # member, moderator, admin
    status: str = Field(default="active") # active, pending, banned
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="memberships")
    community: "Community" = Relationship(back_populates="memberships")

# --- CHAPTERS (Restored for Academy/Library) ---
class Chapter(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    title: str
    description: Optional[str] = None
    sequence_order: int = Field(default=0) # For ordering modules
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    community: "Community" = Relationship(back_populates="chapters")
    posts: List["Post"] = Relationship(back_populates="chapter")

# --- COMMUNITIES ---
class Community(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    
    name: str
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    banner_url: Optional[str] = None
    
    # Archetype & Config
    archetype: Archetype = Field(default=Archetype.DEFAULT)
    config: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON) 
    
    is_private: bool = Field(default=False)
    member_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creator: "User" = Relationship()
    posts: List["Post"] = Relationship(back_populates="community")
    memberships: List["Membership"] = Relationship(back_populates="community")
    chapters: List["Chapter"] = Relationship(back_populates="community")