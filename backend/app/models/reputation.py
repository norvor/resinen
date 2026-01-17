import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User

class ReputationEvent(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    
    source: str         # "social_like", "jury_duty", "course_complete"
    source_id: str      # ID of the post, vote, or course
    
    xp_amount: int      # +10, +500, etc.
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    user: User = Relationship()