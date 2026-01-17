import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class ContentBlock(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Key to identify the block (e.g., "homepage_hero", "about_us_text")
    slug: str = Field(unique=True, index=True) 
    
    # The actual content
    title: Optional[str] = None
    body: Optional[str] = None      # Markdown or HTML
    image_url: Optional[str] = None
    link_text: Optional[str] = None
    link_url: Optional[str] = None
    
    # Metadata
    section: str = Field(default="general") # e.g. "home", "pricing", "footer"
    is_active: bool = Field(default=True)
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)