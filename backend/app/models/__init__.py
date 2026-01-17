from app.models.user import User
from app.models.community import Community, Chapter, Membership
from app.models.social import Post, Comment, PostLike
from app.models.content import ContentBlock
from app.models.referral import MemberService, Vouch
from app.models.academic import AcademicResource
# Make sure these are here:
from app.models.engine import Engine, CommunityEngine 

__all__ = [
    "User", 
    "Community", "Chapter", "Membership", 
    "Post", "Comment", "PostLike",
    "ContentBlock",
    "MemberService", "Vouch",
    "AcademicResource",
    "Engine", "CommunityEngine" # <--- And here
]