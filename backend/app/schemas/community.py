from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# We import the Enum from the model to keep them synced
from app.models.community import Archetype 

class CommunityBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    banner_url: Optional[str] = None
    
    # --- NEW FIELDS ---
    archetype: Archetype = Archetype.DEFAULT
    config: Dict[str, Any] = {} # JSON settings (Tax rate, team names, etc)
    
    is_private: bool = False

class CommunityCreate(CommunityBase):
    pass

class CommunityUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    banner_url: Optional[str] = None
    
    # Allow updating these
    archetype: Optional[Archetype] = None
    config: Optional[Dict[str, Any]] = None
    
    is_private: Optional[bool] = None

class CommunityRead(CommunityBase):
    id: UUID
    creator_id: UUID
    member_count: int
    created_at: datetime
    
    class Config:
        orm_mode = True