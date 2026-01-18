import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.orm import joinedload

from app.api import deps
from app.models.user import User
# FIX 1: Import 'Comment' so we can use it in the query
from app.models.social import Post, PostLike, Comment 
from app.models.community import Membership
from app.models.governance import CommunityBylaw
from app.services.reputation import award_xp, XP_PER_LIKE
from app.schemas.social import PostCreate, PostRead, CommentRead

router = APIRouter()

# --- 1. THE FEED ---
@router.get("/feed", response_model=List[PostRead])
async def get_feed(
    scope: str = Query(..., regex="^(global|community)$"),
    community_id: Optional[uuid.UUID] = None,
    limit: int = 20,
    skip: int = 0,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # FIX 2: Use 'Comment.author' instead of "author"
    query = select(Post).options(
        joinedload(Post.author), 
        joinedload(Post.comments).joinedload(Comment.author) 
    ).order_by(desc(Post.created_at))

    if scope == "community":
        if not community_id:
            raise HTTPException(400, "Community ID required for local feed")
        query = query.where(Post.community_id == community_id)
    
    else: 
        # Global feed logic
        my_communities = select(Membership.community_id).where(
            Membership.user_id == current_user.id,
            Membership.status == "active"
        )
        query = query.where(Post.community_id.in_(my_communities))

    result = await db.execute(query.offset(skip).limit(limit))
    posts = result.scalars().unique().all()

    # B. Get "My Likes"
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

    # C. Manual Mapping
    final_posts = []
    for p in posts:
        formatted_comments = [
            CommentRead(
                id=c.id, content=c.content, author_id=c.author_id,
                author_name=c.author.full_name or "Unknown",
                created_at=c.created_at, post_id=c.post_id
            ) for c in p.comments
        ]

        final_posts.append(
            PostRead(
                id=p.id, community_id=p.community_id, chapter_id=p.chapter_id,
                title=p.title, content=p.content, image_url=p.image_url, link_url=p.link_url,
                is_pinned=p.is_pinned, like_count=p.like_count, 
                comment_count=len(p.comments), view_count=p.view_count, created_at=p.created_at,
                author_id=p.author_id, 
                author_name=p.author.full_name or "Unknown",
                is_liked=(p.id in my_likes),
                comments=formatted_comments
            )
        )

    return final_posts

# --- 2. CREATE POST ---
@router.post("/posts", response_model=PostRead)
async def create_post(
    post_in: PostCreate, 
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # Check Membership
    membership_check = await db.execute(select(Membership).where(
        Membership.user_id == current_user.id,
        Membership.community_id == post_in.community_id,
        Membership.status == "active"
    ))
    if not membership_check.scalars().first():
        raise HTTPException(403, "You are not a citizen of this territory.")

    new_post = Post(
        **post_in.dict(),
        author_id=current_user.id,
        like_count=0, view_count=0
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    return PostRead(
        id=new_post.id, community_id=new_post.community_id, chapter_id=new_post.chapter_id,
        title=new_post.title, content=new_post.content, image_url=new_post.image_url, link_url=new_post.link_url,
        is_pinned=False, like_count=0, comment_count=0, view_count=0, created_at=new_post.created_at,
        author_id=current_user.id, 
        author_name=current_user.full_name or "Me",
        is_liked=False, comments=[]
    )

# --- 3. LIKE POST ---
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
    
    post = await db.get(Post, post_id)
    if post:
        post.like_count += 1
        db.add(post)
    
    await db.commit()
    return {"status": "liked"}