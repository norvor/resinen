import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

class RSVPStatus(str, Enum):
    GOING = "going"
    MAYBE = "maybe"
    NOT_GOING = "not_going"

# --- 1. THE EVENT ---
class ClubEvent(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    cover_image_url: Optional[str] = None
    
    # Logistics
    location_name: str # e.g. "Zoom" or "Central Park"
    start_time: datetime
    end_time: Optional[datetime] = None
    max_attendees: Optional[int] = None
    
    # Stats
    count_going: int = Field(default=0)
    
    # Relationships
    community: "Community" = Relationship()
    creator: "User" = Relationship()

# --- 2. THE RSVP ---
class ClubRSVP(SQLModel, table=True):
    event_id: uuid.UUID = Field(foreign_key="clubevent.id", primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    
    status: RSVPStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)