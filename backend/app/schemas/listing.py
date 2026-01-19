import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.user import UserRead

class ListingBase(BaseModel):
    title: str
    description: str
    price_display: str
    link_url: str
    image_url: Optional[str] = None

class ListingCreate(ListingBase):
    community_id: uuid.UUID

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price_display: Optional[str] = None
    link_url: Optional[str] = None
    image_url: Optional[str] = None

class ListingRead(ListingBase):
    id: uuid.UUID
    community_id: uuid.UUID
    
    domain: Optional[str] = None
    vouch_count: int
    is_verified: bool
    created_at: datetime
    
    # Return the full curator object
    curator: UserRead

    class Config:
        from_attributes = True