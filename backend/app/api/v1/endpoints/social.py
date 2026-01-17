import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

from app.api import deps
from app.models.user import User
from app.models.social import Post, PostLike
from app.models.community import Membership
from app.models.governance import CommunityBylaw
from app.services.reputation import award_xp, XP_PER_LIKE

router = APIRouter()

# --- 1. THE FEED (Global vs Local) ---
@router.get("/feed", response_model=List[Post])
async def get_feed(
    scope: str = Query(..., regex="^(global|community)$"), # 'global' or 'community'
    community_id: Optional[uuid.UUID] = None,
    limit: int = 20,
    skip: int = 0,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    query = select(Post).order_by(desc(Post.created_at))

    if scope == "community":
        if not community_id:
            raise HTTPException(400, "Community ID required for local feed")
        # LOCAL FEED: Only posts from this territory
        query = query.where(Post.community_id == community_id)
    
    else: # scope == "global"
        # GLOBAL FEED: Only posts from communities I am a MEMBER of.
        my_communities = select(Membership.community_id).where(
            Membership.user_id == current_user.id,
            Membership.status == "active"
        )
        query = query.where(Post.community_id.in_(my_communities))

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


# --- 2. POSTING (With Law Enforcement) ---
@router.post("/posts", response_model=Post)
async def create_post(
    post_in: Post, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # A. THE BOUNCER: Are you a member?
    membership_check = await db.execute(select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == post_in.community_id,
        Membership.status == "active"
    ))
    if not membership_check.scalars().first():
        raise HTTPException(403, "You are not a citizen of this territory.")

    # B. THE SHERIFF: Check Bylaws
    bylaws = await db.execute(select(CommunityBylaw).where(
        CommunityBylaw.community_id == post_in.community_id
    ))
    local_laws = {law.rule_key: law.rule_value for law in bylaws.scalars().all()}
    
    if local_laws.get("allow_politics") == "false":
        if "vote" in post_in.title.lower() or "election" in post_in.title.lower():
             raise HTTPException(400, "VIOLATION: Political discourse is banned here.")

    # C. CREATE
    post_in.author_id = current_user.id
    db.add(post_in)
    await db.commit()
    await db.refresh(post_in)
    return post_in

# --- 3. LIKING (With XP Reward) ---
@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # Check if already liked
    existing = await db.execute(select(PostLike).where(
        PostLike.user_id == current_user.id,
        PostLike.post_id == post_id
    ))
    if existing.scalars().first():
        return {"status": "already_liked"}

    # Add Like
    new_like = PostLike(user_id=current_user.id, post_id=post_id)
    db.add(new_like)
    
    # REWARD THE AUTHOR
    post = await db.get(Post, post_id)
    if post and post.author_id != current_user.id:
        await award_xp(
            user_id=post.author_id,
            amount=XP_PER_LIKE,
            source="social_like",
            source_id=str(post_id),
            db=db
        )
    
    await db.commit()
    return {"status": "liked"}