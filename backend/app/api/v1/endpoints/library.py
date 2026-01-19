from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import datetime

from app.core.database import get_session
from app.models.user import User
from app.models.library import LibraryPage
from app.schemas.library import PageRead, PageCreate, PageUpdate, PageTreeItem
from app.api.deps import get_current_user

router = APIRouter()

# --- 1. GET PAGE (By Slug) ---
@router.get("/page/{slug}", response_model=PageRead)
async def get_page(
    slug: str,
    community_id: str,
    db: Session = Depends(get_session)
):
    stmt = select(LibraryPage).where(
        LibraryPage.community_id == community_id,
        LibraryPage.slug == slug
    )
    page = (await db.exec(stmt)).first()
    
    if not page:
        raise HTTPException(404, "Page not found")
        
    return page

# --- 2. GET TREE (Table of Contents) ---
@router.get("/tree", response_model=List[PageTreeItem])
async def get_tree(
    community_id: str,
    db: Session = Depends(get_session)
):
    # Fetch all published pages
    stmt = select(LibraryPage).where(
        LibraryPage.community_id == community_id,
        LibraryPage.is_published == True
    )
    pages = (await db.exec(stmt)).all()
    
    # Build Tree in Python (O(n))
    # 1. Create Map
    nodes = {}
    for p in pages:
        nodes[p.id] = PageTreeItem(id=p.id, slug=p.slug, title=p.title, children=[])
        
    # 2. Link Parents
    roots = []
    for p in pages:
        if p.parent_id and p.parent_id in nodes:
            nodes[p.parent_id].children.append(nodes[p.id])
        else:
            roots.append(nodes[p.id])
            
    return roots

# --- 3. CREATE/UPDATE (Admin/Wiki Mode) ---
@router.post("/", response_model=PageRead)
async def create_page(
    page_in: PageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Check Slug Uniqueness
    existing = await db.exec(select(LibraryPage).where(
        LibraryPage.community_id == page_in.community_id,
        LibraryPage.slug == page_in.slug
    ))
    if existing.first():
        raise HTTPException(400, "Slug already exists in this community")

    new_page = LibraryPage(
        **page_in.dict(),
        author_id=current_user.id
    )
    db.add(new_page)
    await db.commit()
    await db.refresh(new_page)
    return new_page