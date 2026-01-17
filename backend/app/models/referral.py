import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

# Forward reference to avoid circular imports
from app.models.user import User
from app.models.community import Community

class MemberService(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    community_id: uuid.UUID = Field(foreign_key="community.id")
    
    title: str          # e.g., "Criminal Defense Attorney"
    description: str    # e.g., "Specializing in white collar crime..."
    contact_info: str   # e.g., "Email me at..."
    
    # Reputation Metric
    vouch_count: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="services")
    community: Community = Relationship(back_populates="services")
    vouches: List["Vouch"] = Relationship(back_populates="service")

class Vouch(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    service_id: uuid.UUID = Field(foreign_key="memberservice.id")
    voucher_id: uuid.UUID = Field(foreign_key="user.id") # Who is vouching?
    
    comment: Optional[str] = None # e.g., "Raj handled my case perfectly."
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    service: MemberService = Relationship(back_populates="vouches")
    voucher: User = Relationship() # We don't need a back-populate list on User for now