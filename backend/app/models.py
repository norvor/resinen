from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON

# --- SHARED PROPERTIES ---

class ArticleBase(SQLModel):
    title: str
    summary: str
    content: str
    category: str 
    read_time: str = "5 min"
    author: str = "Resinen Ed."
    image_url: Optional[str] = None

class WireItemBase(SQLModel):
    text: str
    type: str = "info"
    created_at: datetime = Field(default_factory=datetime.utcnow)

# --- DATABASE TABLES ---

class Article(ArticleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_published: bool = True

class WireItem(WireItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# --- NEW: UNIVERSAL STORAGE TABLE ---
class UserStorage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str = Field(index=True)
    key: str = Field(index=True)  # e.g., "resinen_projects"
    # Stores ANY JSON data (lists, objects, strings)
    value: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

# --- API RESPONSES ---

class ArticleRead(ArticleBase):
    id: int
    created_at: datetime

class WireItemRead(WireItemBase):
    id: int
    created_at: datetime