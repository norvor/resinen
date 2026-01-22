import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserRead

# --- COMMENT ---
class CommentBase(BaseModel):
    content: str
    parent_id: Optional[uuid.UUID] = None

class CommentCreate(CommentBase):
    pass

class CommentRead(CommentBase):
    id: uuid.UUID
    post_id: uuid.UUID
    like_count: int
    created_at: datetime
    author: UserRead
    is_liked: bool = False # UI State
    
    class Config:
        from_attributes = True

# --- POST ---
class PostBase(BaseModel):
    title: Optional[str] = None
    content: str
    media_urls: List[str] = []
    meta_data: Dict[str, Any] = {}
    chapter_id: Optional[uuid.UUID] = None

class PostCreate(PostBase):
    community_id: uuid.UUID

class PostRead(PostBase):
    id: uuid.UUID
    community_id: uuid.UUID
    
    is_pinned: bool
    like_count: int
    comment_count: int
    view_count: int
    created_at: datetime
    
    author: UserRead
    
    # UI State (Calculated at runtime)
    is_liked: bool = False
    
    class Config:
        from_attributes = True

# --- 🚨 ADDED THIS MISSING CLASS 🚨 ---
class FeedResult(BaseModel):
    items: List[PostRead]
    next_cursor: Optional[str] = None