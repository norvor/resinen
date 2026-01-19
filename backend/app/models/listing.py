import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.user import User

class Listing(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id", index=True)
    curator_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    price_display: str # e.g. "$50" or "Negotiable"
    link_url: str
    image_url: Optional[str] = None
    domain: Optional[str] = None
    
    vouch_count: int = 0
    is_verified: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    curator: "User" = Relationship()

class ListingVouch(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    listing_id: uuid.UUID = Field(foreign_key="listing.id", primary_key=True)