from typing import List
import uuid
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.api import deps
from app.models.library import Page
from app.schemas.library import PageTreeItem

router = APIRouter()

@router.get("/community/{community_id}/tree", response_model=List[PageTreeItem])
async def get_tree(
    community_id: uuid.UUID,
    # 🚨 FIX 1: Change deps.get_db -> deps.get_async_db
    db: AsyncSession = Depends(deps.get_async_db), 
):
    stmt = select(Page).where(Page.community_id == community_id)
    
    # 🚨 FIX 2: Use db.exec() instead of db.execute()
    result = await db.exec(stmt)
    pages = result.all()

    # Build Tree Logic (Python side)
    nodes = {p.id: PageTreeItem.model_validate(p) for p in pages}
    roots = []

    for page in pages:
        node = nodes[page.id]
        if page.parent_id and page.parent_id in nodes:
            nodes[page.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots