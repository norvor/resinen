from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# --- SERVICE LISTING ---
class ServiceCreate(BaseModel):
    community_id: UUID
    title: str
    description: str
    contact_info: str

class ServiceRead(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str
    vouch_count: int
    created_at: datetime

# --- VOUCHING ---
class VouchCreate(BaseModel):
    comment: Optional[str] = None

class VouchRead(BaseModel):
    id: UUID
    voucher_id: UUID
    comment: Optional[str]
    created_at: datetime