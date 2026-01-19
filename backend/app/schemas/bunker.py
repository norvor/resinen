from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class BunkerMessageCreate(BaseModel):
    community_id: UUID
    content: str
    is_anonymous: bool = False
    ttl_seconds: int = 3600 # Default 1 hour

class BunkerMessageRead(BaseModel):
    id: UUID
    content: str
    created_at: datetime
    expires_at: datetime
    
    # If anonymous, we return "Unknown"
    author_name: str
    author_avatar: Optional[str] = None

    class Config:
        from_attributes = True