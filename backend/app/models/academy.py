import uuid
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.community import Community

# --- 1. MODULE (The Chapter) ---
class Module(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    title: str
    description: Optional[str] = None
    order_index: int = Field(default=0) # 0, 1, 2 (Sort order)
    
    # Relationships
    lessons: List["Lesson"] = Relationship(back_populates="module")
    community: "Community" = Relationship()

# --- 2. LESSON (The Content) ---
class Lesson(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    module_id: uuid.UUID = Field(foreign_key="module.id")
    
    title: str
    content_body: str # Markdown or Text
    video_url: Optional[str] = None
    duration_min: int = Field(default=5)
    order_index: int = Field(default=0)
    
    # Relationships
    module: "Module" = Relationship(back_populates="lessons")

# --- 3. PROGRESS (Who finished what) ---
class LessonCompletion(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    lesson_id: uuid.UUID = Field(foreign_key="lesson.id", primary_key=True)
    
    completed_at: datetime = Field(default_factory=datetime.utcnow)