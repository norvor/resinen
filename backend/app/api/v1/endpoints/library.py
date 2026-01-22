from typing import List, Any
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, col

# Models & Schemas
from app.api import deps
from app.models.user import User
from app.models.library import Page  # Assuming this is your model name
from app.schemas.library import PageCreate, PageRead, PageUpdate, PageTreeItem

router = APIRouter()

# --- 1. GET TREE (The function crashing) ---
@router.get("/community/{community_id}/tree", response_model=List[PageTreeItem])
async def get_tree(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db), # 🚨 Fixed Dependency
):
    """
    Fetch all pages for a community and return them as a nested tree.
    """
    # 1. Fetch all pages for this community
    stmt = select(Page).where(Page.community_id == community_id)
    result = await db.exec(stmt) # 🚨 Fixed: Use db.exec()
    pages = result.all()

    # 2. Convert to Dictionary for fast lookup
    # We use a helper to build the tree in Python to avoid complex recursive SQL
    nodes = {p.id: PageTreeItem.model_validate(p) for p in pages}
    roots = []

    # 3. Build Hierarchy
    for page in pages:
        node = nodes[page.id]
        if page.parent_id and page.parent_id in nodes:
            # Add to parent's children
            nodes[page.parent_id].children.append(node)
        else:
            # It's a root node
            roots.append(node)

    return roots

# --- 2. READ SINGLE PAGE ---
@router.get("/{page_id}", response_model=PageRead)
async def read_page(
    page_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
):
    page = await db.get(Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.get("/slug/{community_id}/{slug}", response_model=PageRead)
async def read_page_by_slug(
    community_id: uuid.UUID,
    slug: str,
    db: AsyncSession = Depends(deps.get_async_db),
):
    stmt = select(Page).where(
        Page.community_id == community_id,
        Page.slug == slug
    )
    result = await db.exec(stmt)
    page = result.first()
    
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

# --- 3. CREATE PAGE ---
@router.post("/", response_model=PageRead)
async def create_page(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    page_in: PageCreate,
    current_user: User = Depends(deps.get_current_active_user),
):
    # Check if slug exists in community
    stmt = select(Page).where(
        Page.community_id == page_in.community_id,
        Page.slug == page_in.slug
    )
    existing = await db.exec(stmt)
    if existing.first():
        raise HTTPException(status_code=400, detail="A page with this slug already exists.")

    page = Page(
        **page_in.model_dump(),
        author_id=current_user.id,
        updated_at=None # Sets default
    )
    
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return page

# --- 4. UPDATE PAGE ---
@router.put("/{page_id}", response_model=PageRead)
async def update_page(
    page_id: uuid.UUID,
    page_in: PageUpdate,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    page = await db.get(Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
        
    # Permission check (optional: add logic here)
    
    update_data = page_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(page, key, value)
        
    db.add(page)
    await db.commit()
    await db.refresh(page)
    return page

# --- 5. DELETE PAGE ---
@router.delete("/{page_id}")
async def delete_page(
    page_id: uuid.UUID,
    db: AsyncSession = Depends(deps.get_async_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    page = await db.get(Page, page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    await db.delete(page)
    await db.commit()
    return {"status": "deleted"}