import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

class Listing(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Context
    community_id: uuid.UUID = Field(foreign_key="community.id")
    curator_id: uuid.UUID = Field(foreign_key="user.id") # User who found/posted it
    
    # Product Details
    title: str
    description: str
    price_display: str # e.g. "$199" or "Free". Freeform is better for external items.
    image_url: Optional[str] = None
    
    # The External Destination
    link_url: str 
    domain: Optional[str] = None # e.g. "amazon.com" (We will extract this auto-magically)
    
    # Trust System (Instead of Likes, we use Vouches)
    vouch_count: int = Field(default=0)
    
    # Safety Check (Moderators can mark a link as Safe/Verified)
    is_verified: bool = Field(default=False) 
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    community: "Community" = Relationship()
    curator: "User" = Relationship()

# New Table to track vouches
class ListingVouch(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    listing_id: uuid.UUID = Field(foreign_key="listing.id", primary_key=True)