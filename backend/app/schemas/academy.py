from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

# --- LESSON SCHEMAS ---
class LessonCreate(BaseModel):
    title: str
    content_body: str
    video_url: Optional[str] = None
    duration_min: int
    order_index: int

class LessonRead(BaseModel):
    id: UUID
    title: str
    content_body: str
    video_url: Optional[str]
    duration_min: int
    order_index: int
    
    # Computed for the specific user requesting it
    is_completed: bool = False 

    class Config:
        from_attributes = True

# --- MODULE SCHEMAS ---
class ModuleCreate(BaseModel):
    community_id: UUID
    title: str
    description: str
    order_index: int

class ModuleRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    order_index: int
    lessons: List[LessonRead] = []

    class Config:
        from_attributes = True