from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ContentBlockBase(BaseModel):
    slug: str
    title: Optional[str] = None
    body: Optional[str] = None
    image_url: Optional[str] = None
    link_text: Optional[str] = None
    link_url: Optional[str] = None
    section: str = "general"
    is_active: bool = True

class ContentBlockCreate(ContentBlockBase):
    pass

class ContentBlockUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    image_url: Optional[str] = None
    link_text: Optional[str] = None
    link_url: Optional[str] = None
    is_active: Optional[bool] = None

class ContentBlockRead(ContentBlockBase):
    id: UUID
    updated_at: datetime