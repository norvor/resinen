import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.orm import joinedload # <--- NEEDED FOR AUTHORS

from app.api import deps
from app.models.user import User
# Ensure these match your actual file structure
from app.models.social import Post, PostLike 
from app.models.community import Membership
from app.models.governance import CommunityBylaw
from app.services.reputation import award_xp, XP_PER_LIKE

# --- IMPORT THE SCHEMAS WE MADE EARLIER ---
from app.schemas.social import PostCreate, PostRead, CommentRead 

router = APIRouter()

# --- 1. THE FEED (With Data Transformation) ---
@router.get("/feed", response_model=List[PostRead]) # <--- Returns Clean Schema
async def get_feed(
    scope: str = Query(..., regex="^(global|community)$"),
    community_id: Optional[uuid.UUID] = None,
    limit: int = 20,
    skip: int = 0,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # 1. Build Query with JOIN (To get Author Name)
    query = select(Post).options(
        joinedload(Post.author), 
        joinedload(Post.comments).joinedload("author")
    ).order_by(desc(Post.created_at))

    if scope == "community":
        if not community_id:
            raise HTTPException(400, "Community ID required for local feed")
        query = query.where(Post.community_id == community_id)
    
    else: # scope == "global"
        my_communities = select(Membership.community_id).where(
            Membership.user_id == current_user.id,
            Membership.status == "active"
        )
        query = query.where(Post.community_id.in_(my_communities))

    result = await db.execute(query.offset(skip).limit(limit))
    posts = result.scalars().unique().all()

    # 2. Get "My Likes" (Optimization)
    post_ids = [p.id for p in posts]
    my_likes = set()
    if post_ids:
        likes_result = await db.execute(
            select(PostLike.post_id).where(
                PostLike.user_id == current_user.id,
                PostLike.post_id.in_(post_ids)
            )
        )
        my_likes = set(likes_result.scalars().all())

    # 3. MANUAL MAPPING (DB Object -> Schema)
    final_posts = []
    for p in posts:
        # Map Comments
        formatted_comments = [
            CommentRead(
                id=c.id,
                content=c.content,
                author_id=c.author_id,
                author_name=c.author.full_name or "Unknown", # Flattening
                created_at=c.created_at,
                post_id=c.post_id
            ) for c in p.comments
        ]

        # Map Post
        final_posts.append(
            PostRead(
                id=p.id,
                community_id=p.community_id,
                chapter_id=p.chapter_id,
                title=p.title,
                content=p.content,
                image_url=p.image_url,
                link_url=p.link_url,
                is_pinned=p.is_pinned,
                
                # METRICS
                like_count=p.like_count,
                comment_count=len(p.comments),
                view_count=p.view_count,
                created_at=p.created_at,
                
                # RICH DATA
                author_id=p.author_id,
                author_name=p.author.full_name or "Unknown", # <--- The Frontend needs this!
                is_liked=(p.id in my_likes),                 # <--- The Frontend needs this!
                
                comments=formatted_comments
            )
        )

    return final_posts


# --- 2. POSTING (With Sheriff & Schema) ---
@router.post("/posts", response_model=PostRead) # <--- Input/Output Schemas
async def create_post(
    post_in: PostCreate, # <--- Use Schema for input 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # A. THE BOUNCER
    membership_check = await db.execute(select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == post_in.community_id,
        Membership.status == "active"
    ))
    if not membership_check.scalars().first():
        raise HTTPException(403, "You are not a citizen of this territory.")

    # B. THE SHERIFF
    bylaws = await db.execute(select(CommunityBylaw).where(
        CommunityBylaw.community_id == post_in.community_id
    ))
    local_laws = {law.rule_key: law.rule_value for law in bylaws.scalars().all()}
    
    if local_laws.get("allow_politics") == "false":
        # Check title if exists, otherwise check content
        text_to_check = (post_in.title or "") + " " + post_in.content
        if "vote" in text_to_check.lower() or "election" in text_to_check.lower():
             raise HTTPException(400, "VIOLATION: Political discourse is banned here.")

    # C. CREATE
    new_post = Post(
        **post_in.dict(),
        author_id=current_user.id,
        like_count=0,
        view_count=0
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    # D. Return Schema Format
    return PostRead(
        id=new_post.id,
        community_id=new_post.community_id,
        chapter_id=new_post.chapter_id,
        title=new_post.title,
        content=new_post.content,
        image_url=new_post.image_url,
        link_url=new_post.link_url,
        is_pinned=False,
        like_count=0,
        comment_count=0,
        view_count=0,
        created_at=new_post.created_at,
        author_id=current_user.id,
        author_name=current_user.full_name or "Me",
        is_liked=False,
        comments=[]
    )

# --- 3. LIKING (Kept exactly as you wrote it) ---
@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    existing = await db.execute(select(PostLike).where(
        PostLike.user_id == current_user.id,
        PostLike.post_id == post_id
    ))
    if existing.scalars().first():
        return {"status": "already_liked"}

    new_like = PostLike(user_id=current_user.id, post_id=post_id)
    db.add(new_like)
    
    # Update count on Post object (Optional but good for performance)
    post = await db.get(Post, post_id)
    if post:
        post.like_count += 1
        db.add(post)
        
        # REWARD
        if post.author_id != current_user.id:
            await award_xp(
                user_id=post.author_id,
                amount=XP_PER_LIKE,
                source="social_like",
                source_id=str(post_id),
                db=db
            )
    
    await db.commit()
    return {"status": "liked"}