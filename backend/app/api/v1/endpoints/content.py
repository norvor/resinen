from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api import deps
from app.models.user import User
from app.models.content import ContentBlock
from app.schemas.content import ContentBlockCreate, ContentBlockRead, ContentBlockUpdate

router = APIRouter()

# PUBLIC: Next.js uses this to fetch content
@router.get("/{slug}", response_model=ContentBlockRead)
async def get_content_block(
    slug: str,
    db: AsyncSession = Depends(deps.get_db),
):
    query = select(ContentBlock).where(ContentBlock.slug == slug)
    result = await db.execute(query)
    block = result.scalars().first()
    if not block:
        raise HTTPException(status_code=404, detail="Content block not found")
    return block

# PUBLIC: Fetch all blocks for a section (e.g. "home")
@router.get("/section/{section}", response_model=List[ContentBlockRead])
async def get_section_blocks(
    section: str,
    db: AsyncSession = Depends(deps.get_db),
):
    query = select(ContentBlock).where(ContentBlock.section == section)
    result = await db.execute(query)
    return result.scalars().all()

# PROTECTED: Codex uses this to update content
@router.post("/", response_model=ContentBlockRead)
async def create_content_block(
    block_in: ContentBlockCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser), # Admin Only
):
    block = ContentBlock(**block_in.dict())
    db.add(block)
    await db.commit()
    await db.refresh(block)
    return block

@router.put("/{slug}", response_model=ContentBlockRead)
async def update_content_block(
    slug: str,
    block_in: ContentBlockUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_superuser), # Admin Only
):
    query = select(ContentBlock).where(ContentBlock.slug == slug)
    result = await db.execute(query)
    block = result.scalars().first()
    if not block:
        raise HTTPException(status_code=404, detail="Content block not found")
        
    update_data = block_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(block, key, value)
        
    db.add(block)
    await db.commit()
    await db.refresh(block)
    return block