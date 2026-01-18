from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# We import the Enum from the model to keep them synced
from app.models.community import Archetype 

# --- CHAPTER SCHEMAS (Added Back) ---
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
    id: UUID
    community_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True # Fixed Pydantic V2 warning (was orm_mode)

# --- COMMUNITY SCHEMAS ---

class CommunityBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    banner_url: Optional[str] = None
    archetype: Archetype = Archetype.DEFAULT
    
    # Add installed_engines here too
    config: Dict[str, Any] = {}
    installed_engines: List[str] = [] 
    
    is_private: bool = False

class CommunityCreate(CommunityBase):
    pass

class CommunityUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    banner_url: Optional[str] = None
    
    archetype: Optional[Archetype] = None
    config: Optional[Dict[str, Any]] = None
    
    is_private: Optional[bool] = None

class CommunityRead(CommunityBase):
    id: UUID
    creator_id: UUID
    member_count: int
    created_at: datetime
    
    # Include chapters if loaded
    # chapters: List[ChapterRead] = [] 

    class Config:
        from_attributes = True # Fixed Pydantic V2 warning