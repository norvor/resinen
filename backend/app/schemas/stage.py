from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class VideoCreate(BaseModel):
    community_id: UUID
    title: Optional[str] = None
    video_url: str
    thumbnail_url: str
    duration_sec: int

class VideoRead(BaseModel):
    id: UUID
    title: Optional[str]
    video_url: str
    thumbnail_url: str
    
    view_count: int
    like_count: int
    
    author_name: Optional[str] = None
    author_avatar: Optional[str] = None
    
    created_at: datetime

    class Config:
        from_attributes = True