import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User

if TYPE_CHECKING:
    from app.models.social import Post
    # ADDED: Missing imports
    from app.models.referral import MemberService
    from app.models.academic import AcademicResource

class Community(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    
    creator_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    creator: User = Relationship(back_populates="communities")
    chapters: List["Chapter"] = Relationship(back_populates="community")
    memberships: List["Membership"] = Relationship(back_populates="community")
    
    # ADDED: Fixes referral.py error
    services: List["MemberService"] = Relationship(back_populates="community")
    
    # ADDED: Fixes academic.py error
    academic_resources: List["AcademicResource"] = Relationship(back_populates="community")

class Chapter(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    name: str 
    location: str = Field(default="Global") 
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    community: Community = Relationship(back_populates="chapters")
    memberships: List["Membership"] = Relationship(back_populates="chapter")

class Membership(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    community_id: uuid.UUID = Field(foreign_key="community.id")
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    role: str = Field(default="member")
    
    # Relationships
    user: User = Relationship(back_populates="memberships")
    community: Community = Relationship(back_populates="memberships")
    chapter: Optional[Chapter] = Relationship(back_populates="memberships")