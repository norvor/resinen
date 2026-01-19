import uuid
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

class BunkerMessage(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    author_id: uuid.UUID = Field(foreign_key="user.id")
    
    # Content (Encrypted text could be stored here in future)
    content: str 
    
    # Anonymity (Optional: Hide author name in UI)
    is_anonymous: bool = Field(default=False)
    
    # Ephemeral Logic
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime # The "Burn" time
    
    # Relationships
    community: "Community" = Relationship()
    author: "User" = Relationship()