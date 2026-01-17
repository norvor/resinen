from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class ResourceCreate(BaseModel):
    community_id: UUID
    title: str
    description: Optional[str] = None
    resource_type: str
    url: str

class ResourceRead(BaseModel):
    id: UUID
    community_id: UUID
    title: str
    description: Optional[str]
    resource_type: str
    url: str
    is_verified: bool
    created_at: datetime