from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# --- COMMENTS ---
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: UUID

class CommentRead(CommentBase):
    id: UUID
    author_id: UUID
    author_name: Optional[str] = "Unknown"
    created_at: datetime

# --- POSTS ---
class PostBase(BaseModel):
    content: str
    image_url: Optional[str] = None
    community_id: UUID
    chapter_id: Optional[UUID] = None

class PostCreate(PostBase):
    pass

class PostRead(PostBase):
    id: UUID
    author_id: UUID
    author_name: str 
    
    like_count: int
    is_liked: bool = False # <--- NEW FIELD
    
    created_at: datetime
    comments: List[CommentRead] = []