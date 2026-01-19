import uuid
from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime

from app.api import deps # Consistent dependency injection
from app.models.user import User
from app.models.library import LibraryPage
from app.schemas.library import PageRead, PageCreate, PageUpdate, PageTreeItem

router = APIRouter()

# --- 1. GET PAGE (By Slug) ---
@router.get("/page/{slug}", response_model=PageRead)
async def get_page(
    slug: str,
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    """Retrieve a specific document from the territory library archives."""
    
    # ✅ FIX: Use db.execute() for AsyncSession
    stmt = select(LibraryPage).where(
        LibraryPage.community_id == community_id,
        LibraryPage.slug == slug
    )
    result = await db.execute(stmt)
    page = result.scalars().first()
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found in the archives")
        
    return page

# --- 2. GET TREE (Table of Contents) ---
@router.get("/tree", response_model=List[PageTreeItem])
async def get_tree(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_db)
):
    """Generate the hierarchical map of all published documents."""
    
    # ✅ FIX: Async execution to fetch all published pages
    stmt = select(LibraryPage).where(
        LibraryPage.community_id == community_id,
        LibraryPage.is_published == True
    ).order_by(LibraryPage.title)
    
    result = await db.execute(stmt)
    pages = result.scalars().all()
    
    # Build Tree logic remains O(n) but uses Pydantic v2 model_validate compatibility
    nodes: Dict[uuid.UUID, PageTreeItem] = {}
    
    # 1. Create Map of all nodes
    for p in pages:
        nodes[p.id] = PageTreeItem(
            id=p.id, 
            slug=p.slug, 
            title=p.title, 
            children=[]
        )
        
    # 2. Link Parents to build the structure
    roots = []
    for p in pages:
        if p.parent_id and p.parent_id in nodes:
            nodes[p.parent_id].children.append(nodes[p.id])
        else:
            roots.append(nodes[p.id])
            
    return roots

# --- 3. CREATE PAGE (Publishing) ---
@router.post("/", response_model=PageRead)
async def create_page(
    page_in: PageCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Submit a new document to the library."""
    
    # Check Slug Uniqueness within the community context
    # ✅ FIX: Async execution for uniqueness check
    slug_stmt = select(LibraryPage).where(
        LibraryPage.community_id == page_in.community_id,
        LibraryPage.slug == page_in.slug
    )
    slug_result = await db.execute(slug_stmt)
    if slug_result.scalars().first():
        raise HTTPException(status_code=400, detail="A document with this slug already exists here")

    page_data = page_in.model_dump() if hasattr(page_in, "model_dump") else page_in.dict()
    
    new_page = LibraryPage(
        **page_data,
        author_id=current_user.id,
        created_at=datetime.utcnow()
    )
    
    db.add(new_page)
    await db.commit()
    await db.refresh(new_page)
    return new_page

# --- 4. UPDATE PAGE (Wiki Editing) ---
@router.put("/{page_id}", response_model=PageRead)
async def update_page(
    page_id: uuid.UUID,
    page_up: PageUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
):
    """Edit an existing document. Standard wiki protocol."""
    
    db_page = await db.get(LibraryPage, page_id)
    if not db_page:
        raise HTTPException(status_code=404, detail="Page not found")

    # Update logic (merging fields)
    update_data = page_up.model_dump(exclude_unset=True) if hasattr(page_up, "model_dump") else page_up.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_page, key, value)
    
    db_page.updated_at = datetime.utcnow()
    
    db.add(db_page)
    await db.commit()
    await db.refresh(db_page)
    return db_page