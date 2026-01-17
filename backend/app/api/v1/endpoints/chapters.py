from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from uuid import UUID

from app.api import deps
from app.models.community import Chapter
from app.schemas.community import ChapterCreate, ChapterRead # Import the fixed schema

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