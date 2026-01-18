from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# --- COMMENTS ---
class CommentBase(BaseModel):
    content: str
    parent_id: Optional[UUID] = None # For nested replies

class CommentCreate(CommentBase):
    pass 

class CommentRead(CommentBase):
    id: UUID
    post_id: UUID
    
    # Author Context (Identity Layer)
    author_id: UUID
    author_name: str
    author_avatar: Optional[str] = None
    author_level: int = 1
    
    # Social Proof
    like_count: int
    is_liked: bool = False 
    
    created_at: datetime
    
    class Config:
        orm_mode = True

# --- POSTS ---
class PostBase(BaseModel):
    content: str
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    title: Optional[str] = None
    community_id: UUID
    chapter_id: Optional[UUID] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None

class PostRead(PostBase):
    id: UUID
    
    # Author Context
    author_id: UUID
    author_name: str 
    author_avatar: Optional[str] = None
    author_level: int = 1
    
    # Metrics
    like_count: int
    comment_count: int
    view_count: int = 0
    is_liked: bool = False
    
    created_at: datetime
    
    class Config:
        orm_mode = True