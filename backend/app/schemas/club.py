from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.club import RSVPStatus

class EventCreate(BaseModel):
    community_id: UUID
    title: str
    description: str
    location_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    max_attendees: Optional[int] = None
    cover_image_url: Optional[str] = None

class EventRead(BaseModel):
    id: UUID
    title: str
    description: str
    location_name: str
    start_time: datetime
    end_time: Optional[datetime]
    cover_image_url: Optional[str]
    
    count_going: int
    
    # My Status
    my_rsvp: Optional[RSVPStatus] = None

    class Config:
        from_attributes = True

class RSVPSubmit(BaseModel):
    status: RSVPStatus