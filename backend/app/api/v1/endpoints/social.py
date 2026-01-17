from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.api import deps
from app.models.social import Post, Comment
from app.models.community import Community
from app.models.user import User
from app.schemas.social import PostCreate, PostRead, CommentCreate, CommentRead

router = APIRouter()

@router.get("/feed", response_model=List[PostRead])
async def get_feed(
    community_id: Optional[UUID] = None,
    chapter_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(deps.get_db),
):
    # Build Query
    query = select(Post).options(selectinload(Post.comments)).order_by(desc(Post.created_at))
    
    if community_id:
        query = query.where(Post.community_id == community_id)
    if chapter_id:
        query = query.where(Post.chapter_id == chapter_id)
        
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=PostRead)
async def create_post(
    *,
    db: AsyncSession = Depends(deps.get_db),
    post_in: PostCreate,
    current_user: User = Depends(deps.get_current_user),
):
    # Validate Community
    community = await db.get(Community, post_in.community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    post = Post(
        **post_in.dict(),
        author_id=current_user.id
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

@router.post("/{post_id}/comments", response_model=CommentRead)
async def create_comment(
    post_id: UUID,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    comment = Comment(
        **comment_in.dict(),
        post_id=post_id,
        author_id=current_user.id
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment