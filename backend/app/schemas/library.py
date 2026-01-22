import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# --- WRITE SCHEMAS ---
class PageCreate(BaseModel):
    community_id: uuid.UUID
    title: str
    slug: str
    content: str
    parent_id: Optional[uuid.UUID] = None

class PageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    is_published: Optional[bool] = None

# --- READ SCHEMAS ---
class PageRead(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    content: str
    parent_id: Optional[uuid.UUID]
    updated_at: datetime
    
    # Author info (populated manually or via join)
    author_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- TREE VIEW SCHEMA ---
class PageTreeItem(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    children: List["PageTreeItem"] = []
    
    class Config:
        from_attributes = True