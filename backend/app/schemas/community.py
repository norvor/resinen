import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserRead

# --- CHAPTERS ---
class ChapterBase(BaseModel):
    title: str
    description: Optional[str] = None
    sequence_order: int = 0

class ChapterCreate(ChapterBase):
    pass

class ChapterUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sequence_order: Optional[int] = None

class ChapterRead(ChapterBase):
    id: uuid.UUID
    community_id: uuid.UUID
    
    class Config:
        from_attributes = True

# --- MEMBERSHIP ---
class MembershipBase(BaseModel):
    role: str = "member"
    status: str = "active"

class MembershipCreate(MembershipBase):
    user_id: uuid.UUID
    community_id: uuid.UUID

class MembershipOut(MembershipBase):
    joined_at: datetime
    user_id: uuid.UUID
    community_id: uuid.UUID
    
    # Nested User Profile for Admin Tables
    user: Optional[UserRead] = None
    
    class Config:
        from_attributes = True

# --- COMMUNITY ---
class CommunityBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    banner_url: Optional[str] = None
    icon_url: Optional[str] = None
    primary_color: str = "#000000"
    is_private: bool = False

class CommunityCreate(CommunityBase):
    # Pass 'archetypes' as a list of strings
    archetypes: List[str] = []

class CommunityUpdate(CommunityBase):
    name: Optional[str] = None
    slug: Optional[str] = None
    config: Dict[str, Any] = {}
    installed_engines: List[str] = []

class CommunityRead(CommunityBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    member_count: int
    created_at: datetime
    
    # JSON Fields
    config: Dict[str, Any] = {}
    installed_engines: List[str] = []
    
    class Config:
        from_attributes = True