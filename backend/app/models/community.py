import uuid
from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON

# Forward reference for type hinting
from .user import User

class Community(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    slug: str = Field(unique=True, index=True)
    description: str
    settings: Dict = Field(default={}, sa_column=Column(JSON))
    
    services: List["MemberService"] = Relationship(back_populates="community")
    academic_resources: List["AcademicResource"] = Relationship(back_populates="community")
    chapters: List["Chapter"] = Relationship(back_populates="community")
    memberships: List["Membership"] = Relationship(back_populates="community")

class Chapter(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    community_id: uuid.UUID = Field(foreign_key="community.id")
    location: str
    
    community: Community = Relationship(back_populates="chapters")
    memberships: List["Membership"] = Relationship(back_populates="chapter")

class Membership(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    community_id: uuid.UUID = Field(foreign_key="community.id")
    chapter_id: Optional[uuid.UUID] = Field(default=None, foreign_key="chapter.id")
    role: str = Field(default="member")
    
    user: User = Relationship(back_populates="memberships")
    community: Community = Relationship(back_populates="memberships")
    chapter: Optional[Chapter] = Relationship(back_populates="memberships")