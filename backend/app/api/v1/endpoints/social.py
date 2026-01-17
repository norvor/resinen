from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, col
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.api import deps
from app.models.user import User
from app.models.social import Post, Comment, PostLike
from app.schemas.social import PostCreate, PostRead, CommentCreate, CommentRead

router = APIRouter()

# --- POSTS ---

@router.post("/", response_model=PostRead)
async def create_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    post = Post(**post_in.dict(), author_id=current_user.id)
    db.add(post)
    await db.commit()
    
    await db.refresh(post)
    await db.refresh(post, ["author"]) 
    
    return PostRead(
        **post.dict(),
        author_name=post.author.full_name,
        comments=[],
        is_liked=False
    )

@router.get("/", response_model=List[PostRead])
async def get_feed(
    community_id: UUID,
    chapter_id: UUID = None,
    limit: int = 50,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    # 1. Fetch Posts
    query = (
        select(Post)
        .where(Post.community_id == community_id)
        .options(
            selectinload(Post.author),
            selectinload(Post.comments).selectinload(Comment.author)
        )
        .order_by(col(Post.created_at).desc())
        .limit(limit)
    )
    if chapter_id:
        query = query.where(Post.chapter_id == chapter_id)
    
    result = await db.execute(query)
    posts = result.scalars().all()

    # 2. Fetch User's Likes (Efficiency Optimization)
    # Instead of N+1 queries, we fetch all IDs the user liked in this batch
    post_ids = [p.id for p in posts]
    liked_query = select(PostLike.post_id).where(
        PostLike.user_id == current_user.id,
        PostLike.post_id.in_(post_ids)
    )
    liked_result = await db.execute(liked_query)
    liked_ids = set(liked_result.scalars().all())

    # 3. Map Results
    return [
        PostRead(
            **post.dict(), 
            author_name=post.author.full_name if post.author else "Unknown",
            is_liked=(post.id in liked_ids), # Check against the set
            comments=[
                CommentRead(
                    **c.dict(),
                    author_name=c.author.full_name if c.author else "Unknown"
                ) for c in post.comments
            ]
        ) 
        for post in posts
    ]

# --- COMMENTS ---

@router.post("/comments", response_model=CommentRead)
async def create_comment(
    comment_in: CommentCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    post = await db.get(Post, comment_in.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(**comment_in.dict(), author_id=current_user.id)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    await db.refresh(comment, ["author"])
    
    return CommentRead(**comment.dict(), author_name=comment.author.full_name)

# --- LIKES (NEW) ---

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if already liked
    existing_like = await db.get(PostLike, (current_user.id, post_id))

    if existing_like:
        # Unlike
        await db.delete(existing_like)
        post.like_count = max(0, post.like_count - 1)
        is_liked = False
    else:
        # Like
        new_like = PostLike(user_id=current_user.id, post_id=post_id)
        db.add(new_like)
        post.like_count += 1
        is_liked = True

    db.add(post)
    await db.commit()
    
    return {"like_count": post.like_count, "is_liked": is_liked}