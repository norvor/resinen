# 1. Load User (Independent)
from app.models.user import User

# 2. Load Engines (Must load BEFORE Community because Community links to it)
from app.models.engine import Engine, CommunityEngine 

# 3. Load Community (Now it can find "CommunityEngine")
from app.models.community import Community, Chapter, Membership

# 4. Load Everything Else
from app.models.social import Post, Comment, PostLike
from app.models.content import ContentBlock
from app.models.referral import MemberService, Vouch
from app.models.academic import AcademicResource

__all__ = [
    "User", 
    "Engine", "CommunityEngine", # Moved up
    "Community", "Chapter", "Membership", 
    "Post", "Comment", "PostLike",
    "ContentBlock",
    "MemberService", "Vouch",
    "AcademicResource",
]