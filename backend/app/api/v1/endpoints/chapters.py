from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID

from app.api import deps
from app.models.community import Chapter, Community
from app.schemas.community import ChapterCreate, ChapterRead, ChapterUpdate # Import the fixed schema

router = APIRouter()

# FIX: response_model=List[ChapterRead] ensures the schema is applied
@router.get("/", response_model=List[ChapterRead])
async def get_chapters(
    community_id: UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    query = select(Chapter).where(Chapter.community_id == community_id)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=ChapterRead)
async def create_chapter(
    chapter_in: ChapterCreate,
    db: AsyncSession = Depends(deps.get_db)
):
    chapter = Chapter(**chapter_in.dict())
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    return chapter

@router.get("/{chapter_id}", response_model=ChapterRead)
async def get_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(deps.get_db),
):
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter

@router.put("/{chapter_id}", response_model=ChapterRead)
async def update_chapter(
    chapter_id: str,
    chapter_in: ChapterUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Permission: Check if user owns the community
    community = await db.get(Community, chapter.community_id)
    if community.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = chapter_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(chapter, key, value)

    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)
    return chapter

@router.delete("/{chapter_id}")
async def delete_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    chapter = await db.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    community = await db.get(Community, chapter.community_id)
    if community.creator_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(chapter)
    await db.commit()
    return {"status": "deleted"}