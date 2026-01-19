import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class RSVPStatus(str, Enum):
    GOING = "going"
    MAYBE = "maybe"
    NOT_GOING = "not_going"

class ClubEvent(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    description: str
    location_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    cover_image_url: Optional[str] = None
    
    count_going: int = 0

class ClubRSVP(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    event_id: uuid.UUID = Field(foreign_key="clubevent.id", primary_key=True)
    status: RSVPStatus = Field(default=RSVPStatus.GOING)