from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class PageCreate(BaseModel):
    community_id: UUID
    title: str
    slug: str
    content: str
    parent_id: Optional[UUID] = None

class PageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    is_published: Optional[bool] = None

class PageRead(BaseModel):
    id: UUID
    slug: str
    title: str
    content: str
    parent_id: Optional[UUID]
    updated_at: datetime
    author_name: Optional[str] = None

    class Config:
        from_attributes = True

# For the Sidebar (Tree View)
class PageTreeItem(BaseModel):
    id: UUID
    slug: str
    title: str
    children: List["PageTreeItem"] = []