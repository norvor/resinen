import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class PageCreate(BaseModel):
    community_id: uuid.UUID
    title: str
    slug: str
    content: str
    parent_id: Optional[uuid.UUID] = None

class PageRead(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    content: str
    parent_id: Optional[uuid.UUID]
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Recursive Schema for the "Folder Tree" sidebar
class PageTreeItem(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    children: List["PageTreeItem"] = []
    
    class Config:
        from_attributes = True