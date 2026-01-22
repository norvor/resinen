import uuid
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    
    full_name: str = Field(default="Operator")
    avatar_url: str = Field(default="")
    
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)