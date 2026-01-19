import uuid
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserRead

# --- COMMENT ---
class CommentBase(BaseModel):
    content: str
    parent_id: Optional[uuid.UUID] = None

class CommentCreate(CommentBase):
    post_id: uuid.UUID

class CommentRead(CommentBase):
    id: uuid.UUID
    post_id: uuid.UUID
    like_count: int
    created_at: datetime
    
    author: UserRead
    
    class Config:
        from_attributes = True

# --- POST ---
class PostBase(BaseModel):
    title: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    link_url: Optional[str] = None
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
    
    class Config:
        from_attributes = True