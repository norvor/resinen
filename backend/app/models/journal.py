import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.models.user import User

class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entry"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    
    content: str
    media_urls: List[str] = Field(default=[], sa_type=JSONB)
    tags: List[str] = Field(default=[], sa_type=JSONB)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # It's personal, but you might want to "star" good memories
    is_favorite: bool = Field(default=False)
    stickers: List[Dict] = Field(default=[], sa_column=Column(JSON))
    
    # Relationship
    user: User = Relationship()