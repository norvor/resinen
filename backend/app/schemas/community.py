from typing import Optional
from uuid import UUID
from pydantic import BaseModel

# --- COMMUNITY ---
class CommunityBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    is_private: bool = False  # <--- FIX 1: Add this here so it exists by default

class CommunityCreate(CommunityBase):
    pass 
    # Since it inherits from Base, it now accepts 'is_private'

class CommunityRead(CommunityBase):
    id: UUID
    # It inherits 'is_private', so the Frontend will now see the lock icon correctly.
    member_count: int = 0 # Optional: Useful for dashboard stats
    creator_id: Optional[UUID] = None  # <--- NEW FIELD: Essential for permissions

    class Config:
        from_attributes = True

class CommunityUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None # <--- FIX 2: Allow changing privacy later

# --- CHAPTER ---
class ChapterCreate(BaseModel):
    community_id: UUID
    name: str
    location: str 

class ChapterRead(BaseModel):
    id: UUID
    community_id: UUID
    name: str
    location: Optional[str] = None

class ChapterUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None