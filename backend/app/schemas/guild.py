from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from app.models.guild import BountyStatus

# --- PROJECT SCHEMAS ---
class ProjectCreate(BaseModel):
    community_id: UUID
    title: str
    description: str
    repo_url: Optional[str] = None
    demo_url: Optional[str] = None
    tech_stack: Optional[str] = None

class ProjectRead(BaseModel):
    id: UUID
    title: str
    description: str
    repo_url: Optional[str]
    demo_url: Optional[str]
    tech_stack: Optional[str]
    likes: int
    
    author_name: str
    author_avatar: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- BOUNTY SCHEMAS ---
class BountyCreate(BaseModel):
    community_id: UUID
    title: str
    description: str
    reward_text: str

class BountyRead(BaseModel):
    id: UUID
    title: str
    description: str
    reward_text: str
    status: BountyStatus
    applicant_count: int
    
    author_name: str
    author_avatar: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True