import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import joinedload

from app.api import deps # Consistent dependency injection
from app.models.user import User
from app.models.stage import StageVideo
from app.schemas.stage import VideoRead, VideoCreate

router = APIRouter()

# --- 1. GET FEED (Infinite Scroll) ---
@router.get("/", response_model=List[VideoRead])
async def get_stage_feed(
    community_id: uuid.UUID,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(deps.get_db)
):
    """Fetch the spotlight feed for the territory's Stage."""
    
    # ✅ FIX: Use joinedload(StageVideo.author) to prevent async lazy-load errors
    # Algorithmic sorting can be added here later (e.g., by view_count/age)
    stmt = (
        select(StageVideo)
        .options(joinedload(StageVideo.author))
        .where(StageVideo.community_id == community_id)
        .order_by(StageVideo.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    # ✅ FIX: Proper Async execution for the video list
    result = await db.execute(stmt)
    videos = result.scalars().all()
    
    results = []
    for v in videos:
        # Pydantic v2 model_validate or v1 from_orm
        v_read = VideoRead.model_validate(v) if hasattr(VideoRead, "model_validate") else VideoRead.from_orm(v)
        
        # Populate Author data from the pre-joined relation
        v_read.author_name = v.author.full_name if v.author else "Independent Creator"
        v_read.author_avatar = v.author.avatar_url if v.author else None
        results.append(v_read)
        
    return results

# --- 2. UPLOAD VIDEO (Metadata Only) ---
@router.post("/", response_model=VideoRead)
async def post_video(
    vid_in: VideoCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Submit a new video entry to the Stage."""
    
    vid_data = vid_in.model_dump() if hasattr(vid_in, "model_dump") else vid_in.dict()
    
    new_vid = StageVideo(
        **vid_data,
        author_id=current_user.id,
        view_count=0
    )
    
    db.add(new_vid)
    await db.commit()
    await db.refresh(new_vid)
    
    # Return formatted for the "Paper" UI
    res = VideoRead.model_validate(new_vid) if hasattr(VideoRead, "model_validate") else VideoRead.from_orm(new_vid)
    res.author_name = current_user.full_name
    res.author_avatar = current_user.avatar_url
    return res

# --- 3. VIEW COUNT (Heartbeat) ---
@router.post("/{video_id}/view", response_model=Any)
async def record_view(
    video_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    """Register a view event. Essential for algorithmic 'Awesome' ranking."""
    
    # ✅ FIX: Standard async db.get
    vid = await db.get(StageVideo, video_id)
    if not vid:
        raise HTTPException(status_code=404, detail="Performance (Video) not found")
        
    vid.view_count += 1
    db.add(vid)
    await db.commit()
    
    return {"status": "ok", "total_views": vid.view_count}