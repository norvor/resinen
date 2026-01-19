from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, HttpUrl

class ListingBase(BaseModel):
    title: str
    description: str
    price_display: str
    link_url: str # Pydantic will validate this is a URL
    image_url: Optional[str] = None

class ListingCreate(ListingBase):
    community_id: UUID

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price_display: Optional[str] = None
    link_url: Optional[str] = None
    image_url: Optional[str] = None

class ListingRead(ListingBase):
    id: UUID
    community_id: UUID
    curator_id: UUID
    
    # Flattened Curator Info (Easy for frontend)
    curator_name: Optional[str] = None 
    curator_avatar: Optional[str] = None
    
    domain: Optional[str] = None
    vouch_count: int
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True