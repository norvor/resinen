from pydantic import BaseModel
from typing import Optional, Dict
from uuid import UUID

class CommunityCreate(BaseModel):
    name: str
    slug: str
    description: str
    settings: Optional[Dict] = {}

class CommunityRead(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str
    settings: Dict

class ChapterCreate(BaseModel):
    community_id: UUID
    location_name: str

class ChapterRead(BaseModel):
    id: UUID
    location_name: str
    community_id: UUID