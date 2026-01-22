import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class JournalBase(BaseModel):
    content: str
    media_urls: List[str] = []
    tags: List[str] = []
    is_favorite: bool = False

class JournalCreate(JournalBase):
    pass

class JournalUpdate(BaseModel):
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None

class JournalRead(JournalBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime # Track edits
    
    class Config:
        from_attributes = True