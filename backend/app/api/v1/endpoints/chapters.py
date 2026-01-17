from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID

from app.api import deps
from app.models.community import Chapter, Community
from app.models.user import User
from app.schemas.community import ChapterCreate, ChapterRead

router = APIRouter()

@router.get("/", response_model=List[ChapterRead])
async def read_chapters(
    skip: int = 0,
    limit: int = 100,
    community_id: UUID = None, # Optional filter
    db: AsyncSession = Depends(deps.get_db),
):
    query = select(Chapter)
    if community_id:
        query = query.where(Chapter.community_id == community_id)
        
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=ChapterRead)
async def create_chapter(
    *,
    db: AsyncSession = Depends(deps.get_db),
    chapter_in: ChapterCreate,
    current_user: User = Depends(deps.get_current_user), # <--- Protected!
):
    # 1. Check if Community exists
    community = await db.get(Community, chapter_in.community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")
        
    # 2. Create Chapter
    db_chapter = Chapter.from_orm(chapter_in)
    db.add(db_chapter)
    await db.commit()
    await db.refresh(db_chapter)
    return db_chapter