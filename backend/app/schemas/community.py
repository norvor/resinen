from typing import Optional
from uuid import UUID
from pydantic import BaseModel

# --- COMMUNITY ---
class CommunityBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class CommunityCreate(CommunityBase):
    pass

class CommunityRead(CommunityBase):
    id: UUID

# --- CHAPTER ---
class ChapterCreate(BaseModel):
    community_id: UUID
    name: str
    location_name: str 

# FIX: This tells the backend exactly what to return
class ChapterRead(BaseModel):
    id: UUID
    community_id: UUID
    name: str                     # <--- This was likely missing or hidden
    location_name: Optional[str] = None