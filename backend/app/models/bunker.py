import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from app.models.user import User

class BunkerMessage(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id", index=True)
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    content: str
    is_anonymous: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime 
    
    author: "User" = Relationship()