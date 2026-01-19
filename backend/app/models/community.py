import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import JSON 

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.social import Post

# Keep Enum for validation, even if DB stores strings
class Archetype(str, Enum):
    # original
    SANCTUARY = "sanctuary" 
    BAZAAR = "bazaar"
    SENATE = "senate"
    ARENA = "arena"
    
    # NEW ENGINES (Add these lines)
    ACADEMY = "academy"   # Engine 3
    CLUB = "club"         # Engine 5
    LIBRARY = "library"   # Engine 6
    STAGE = "stage"       # Engine 7
    BUNKER = "bunker"     # Engine 8
    GUILD = "guild"       # Engine 9
    GARDEN = "garden"     # Engine 10
    
    # Generic/Mixed
    LOUNGE = "lounge"     
    SPOTLIGHT = "spotlight" # Optional alias for Stage

# --- MEMBERSHIPS ---
class Membership(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id", primary_key=True)
    role: str = Field(default="member")
    status: str = Field(default="active")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: "User" = Relationship(back_populates="memberships")
    community: "Community" = Relationship(back_populates="memberships")

# --- CHAPTERS ---
class Chapter(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    title: str
    description: Optional[str] = None
    sequence_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
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
    
    # 🚨 CHANGED: From Single Enum to List of Strings (JSON)
    archetypes: List[str] = Field(default_factory=list, sa_type=JSON)
    
    # --- CONFIG & ENGINES ---
    config: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    installed_engines: List[str] = Field(default_factory=list, sa_type=JSON)

    is_private: bool = Field(default=False)
    member_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creator: "User" = Relationship()
    posts: List["Post"] = Relationship(back_populates="community")
    memberships: List["Membership"] = Relationship(back_populates="community")
    chapters: List["Chapter"] = Relationship(back_populates="community")