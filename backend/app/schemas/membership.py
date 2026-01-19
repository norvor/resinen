from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

# 1. Define what User details are safe to share (No passwords!)
class UserInMembership(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None  # Added this as it's often needed for UI
    
    class Config:
        from_attributes = True

# 2. Define the Membership output that INCLUDES the User
class MembershipOut(BaseModel):
    # ❌ REMOVED: id field (It does not exist in your composite-key table)
    
    user_id: UUID
    community_id: UUID
    role: str
    status: str
    joined_at: datetime
    
    # The magic field for the Admin Panel / UI
    user: Optional[UserInMembership] = None 

    class Config:
        from_attributes = True