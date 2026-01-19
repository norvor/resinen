import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship

class StageVideo(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    title: str
    video_url: str # YouTube/Twitch Embed
    thumbnail_url: str
    duration_sec: int = 0
    
    view_count: int = 0
    like_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)