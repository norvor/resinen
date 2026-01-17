from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime
import uuid

# --- 1. USERS (Global Identity) ---
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str
    avatar_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    memberships: List["Membership"] = Relationship(back_populates="user")

# --- 2. COMMUNITIES (The "Worlds") ---
class Community(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str  # e.g., "Legal Community"
    slug: str = Field(unique=True, index=True) # e.g., "legal"
    description: str
    
    # Settings: JSON to hold "Bylaws", "Enabled Features", "Theme Colors"
    settings: dict = Field(default={}, sa_column=Column(JSON))

    # Relationships
    chapters: List["Chapter"] = Relationship(back_populates="community")
    memberships: List["Membership"] = Relationship(back_populates="community")

# --- 3. CHAPTERS (The Physical Link) ---
class Chapter(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    location_name: str # e.g., "Mumbai", "London"
    geo_lat: Optional[float] = None
    geo_long: Optional[float] = None
    
    # Relationships
    community: Community = Relationship(back_populates="chapters")
    memberships: List["Membership"] = Relationship(back_populates="chapter")

# --- 4. MEMBERSHIPS (The "Persona" & Access Control) ---
class Membership(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    user_id: uuid.UUID = Field(foreign_key="user.id")
    community_id: uuid.UUID = Field(foreign_key="community.id")
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    
    # Role: 'member', 'moderator', 'admin'
    role: str = Field(default="member")
    
    # Reputation: Specific to THIS community
    reputation_score: int = Field(default=0)
    
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="memberships")
    community: Community = Relationship(back_populates="memberships")
    chapter: Optional[Chapter] = Relationship(back_populates="memberships")