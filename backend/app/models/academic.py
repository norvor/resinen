import uuid
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.community import Community

class AcademicResource(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    title: str
    description: Optional[str] = None
    resource_type: str  # 'paper', 'course', 'video', 'template'
    url: str            # Link to PDF/Video
    is_verified: bool = Field(default=False) # True if peer-reviewed
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    community: Community = Relationship(back_populates="academic_resources")