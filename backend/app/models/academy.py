import uuid
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

class Module(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    title: str
    description: Optional[str] = None
    order_index: int = 0
    
    lessons: List["Lesson"] = Relationship(back_populates="module")

class Lesson(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    module_id: uuid.UUID = Field(foreign_key="module.id")
    
    title: str
    content_body: str
    video_url: Optional[str] = None
    duration_min: int = 0
    order_index: int = 0
    
    module: "Module" = Relationship(back_populates="lessons")

class LessonCompletion(SQLModel, table=True):
    user_id: uuid.UUID = Field(foreign_key="user.id", primary_key=True)
    lesson_id: uuid.UUID = Field(foreign_key="lesson.id", primary_key=True)
    completed_at: datetime = Field(default_factory=datetime.utcnow)