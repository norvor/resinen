from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# --- COMMENTS ---
class CommentCreate(BaseModel):
    content: str

class CommentRead(BaseModel):
    id: UUID
    author_id: UUID
    content: str
    created_at: datetime

# --- POSTS ---
class PostCreate(BaseModel):
    community_id: UUID
    chapter_id: Optional[UUID] = None
    content: str
    image_url: Optional[str] = None

class PostRead(BaseModel):
    id: UUID
    author_id: UUID
    community_id: UUID
    chapter_id: Optional[UUID]
    content: str
    image_url: Optional[str]
    like_count: int
    created_at: datetime
    # We return the last 3 comments for preview, or fetch separately
    comments: List[CommentRead] = []