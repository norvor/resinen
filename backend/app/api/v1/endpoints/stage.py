from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from app.core.database import get_session
from app.models.user import User
from app.models.stage import StageVideo
from app.schemas.stage import VideoRead, VideoCreate
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. GET FEED (Infinite Scroll) ---
@router.get("/", response_model=List[VideoRead])
async def get_stage_feed(
    community_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_session)
):
    # For "The Stage", random ordering or algorithmic is best,
    # but for MVP we do newest first.
    stmt = (
        select(StageVideo)
        .where(StageVideo.community_id == community_id)
        .order_by(StageVideo.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    videos = (await db.exec(stmt)).all()
    
    results = []
    for v in videos:
        v_read = VideoRead.from_orm(v)
        # Populate Author (Assuming simple load)
        v_read.author_name = v.author.full_name if v.author else "Creator"
        v_read.author_avatar = v.author.avatar_url if v.author else None
        results.append(v_read)
        
    return results

# --- 2. UPLOAD VIDEO (Metadata Only) ---
@router.post("/", response_model=VideoRead)
async def post_video(
    vid_in: VideoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    new_vid = StageVideo(
        **vid_in.dict(),
        author_id=current_user.id
    )
    db.add(new_vid)
    await db.commit()
    await db.refresh(new_vid)
    
    # Return with Author info
    res = VideoRead.from_orm(new_vid)
    res.author_name = current_user.full_name
    res.author_avatar = current_user.avatar_url
    return res

# --- 3. VIEW COUNT (Heartbeat) ---
@router.post("/{video_id}/view", response_model=Any)
async def record_view(
    video_id: str,
    db: Session = Depends(get_session)
):
    # This is a "Fire and Forget" endpoint usually
    vid = await db.get(StageVideo, video_id)
    if vid:
        vid.view_count += 1
        db.add(vid)
        await db.commit()
    return {"status": "ok"}