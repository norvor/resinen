# This file registers all models so SQLModel can find them
from app.models.user import User
from app.models.community import Community, Chapter, Membership
from app.models.social import Post, Comment, PostLike
from app.models.content import ContentBlock
from app.models.marketing import (
    MarketingHomepage, 
    MarketingEngine, 
    MarketingPost, 
    MarketingConfig
)

# Export them for cleaner imports elsewhere
__all__ = [
    "User", 
    "Community", "Chapter", "Membership", 
    "Post", "Comment", "PostLike",
    "ContentBlock",
    "MarketingHomepage", "MarketingEngine", "MarketingPost", "MarketingConfig"
]